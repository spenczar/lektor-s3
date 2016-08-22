# -*- coding: utf-8 -*-
import mimetypes
import os
import posixpath
import time
from hashlib import md5

from lektor.publisher import Publisher, PublishError
from lektor.pluginsystem import Plugin

import boto3
import botocore.exceptions


class S3Plugin(Plugin):
    name = u's3'
    description = u'Adds S3 as a deploy target. Use s3://<bucket> to deploy to a bucket.'

    def on_setup_env(self, **extra):
        # Modern Lektor stores publishers in env
        if hasattr(self.env, 'publishers'):
            self.env.publishers['s3'] = S3Publisher
        # Older versions stored publishers in a global
        else:
            from lektor.publisher import publishers
            publishers['s3'] = S3Publisher


class S3Publisher(Publisher):
    def __init__(self, env, output_path):
        super(S3Publisher, self).__init__(env, output_path)
        self.s3 = None
        self.bucket = None
        self.key_prefix = ''
        self.cloudfront = None

    def split_bucket_uri(self, target_url):
        bucket = target_url.netloc
        key = target_url.path
        if key != '':
            if key.startswith('/'):
                key = key[1:]
            if not key.endswith('/'):
                key = key + '/'
        return bucket, key

    def verify_bucket_exists(self):
        exists = True
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket.name)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                exists = False
        return exists

    def list_remote(self):
        return self.bucket.objects.filter(Prefix=self.key_prefix)

    def list_local(self):
        all_files = []
        for path, _, files in os.walk(self.output_path):
            for f in files:
                fullpath = os.path.join(path, f)
                relpath = os.path.relpath(fullpath, self.output_path)
                if os.path.dirname(relpath) != ".lektor":
                    all_files.append(os.path.relpath(fullpath, self.output_path))

        return all_files

    def file_md5(self, filename):
        '''Compute the md5 checksum for a file.'''
        md5sum = md5()
        with open(filename, 'rb') as f:
            data = f.read(8192)
            while len(data) > 0:
                md5sum.update(data)
                data = f.read(8192)
        return md5sum.hexdigest()

    def obj_md5(self, obj):
        """Compute the md5 checksum for an S3 object.

        MD5s can be stored in the 'ETag' field of S3 objects. The
        field doesn't store the MD5 in two cases: objects uploaded
        with Multipart Upload and objects encrypted with SSE-C or
        SSE-KMS. In those cases, we'll just return an empty string.

        """

        # Multipart-uploaded messages have etags that look like 'xxx-nnn'
        if '-' in obj.e_tag:
            return ''

        # SSE-C and SSE-KMS-encrypted objects have a few values set
        # when you call HeadObject on them
        obj_meta = self.s3.meta.client.head_object(
            Bucket=obj.bucket_name,
            Key=obj.key,
        )
        if obj_meta.get('SSECustomerAlgorithm') is not None:
            return ''
        if obj_meta.get('ServerSideEncryption') == 'aws:kms':
            return ''

        # Else, the etag stores an md5 checksum enclosed in double quotes
        return obj.e_tag.strip('"')

    def different(self, local_filename, remote_obj):
        """Return true if the local file is different than the remote object."""
        abs_filename = os.path.join(self.output_path, local_filename)
        # Check size first.
        if remote_obj.size != os.path.getsize(abs_filename):
            return True

        # check md5
        if self.file_md5(abs_filename) != self.obj_md5(remote_obj):
            return True

        # they're the same
        return False

    def compute_diff(self, local, remote):
        """Compute the changeset for updating remote to match local"""
        diff = {
            'add': [],
            'update': [],
            'delete': [],
        }
        remote_keys = {o.key: o for o in remote}
        local_keys = []
        for f in local:
            key = posixify(self.key_prefix + f)
            if key in remote_keys:
                if self.different(f, remote_keys[key]):
                    diff['update'].append(f)
            else:
                diff['add'].append(f)
            local_keys.append(key)
        for k in remote_keys:
            if k not in local_keys:
                diff['delete'].append(k)
        return diff

    def add(self, filename):
        abs_filename = os.path.join(self.output_path, filename)
        key = self.key_prefix + filename

        mime, _ = mimetypes.guess_type(filename)
        if mime is None:
            mime = "text/plain"
        self.bucket.upload_file(abs_filename, posixify(key), ExtraArgs={'ContentType': mime})

    def update(self, filename):
        # Updates are just overwrites in S3
        self.add(filename)

    def delete_batch(self, filenames):
        if len(filenames) == 0:
            return
        self.bucket.delete_objects(
            Delete={'Objects': [{'Key': self.key_prefix + f} for f in filenames]}
        )

    def invalidate_cloudfront(self, distribution_id):
        if not distribution_id:
            return

        ref = "lektor{time}".format(time=time.time())
        path = "/{prefix}*".format(prefix=self.key_prefix)
        self.cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [path],
                },
                'CallerReference': ref,
            }
        )
        yield 'invalidated all paths in CloudFront'

    def connect(self, credentials):
        self.s3 = boto3.resource(service_name='s3')
        self.cloudfront = boto3.client(service_name='cloudfront')

    def publish(self, target_url, credentials=None, server_info=None, **extra):
        if credentials is None:
            credentials = {}
        self.connect(credentials)

        bucket_uri, self.key_prefix = self.split_bucket_uri(target_url)
        self.bucket = self.s3.Bucket(bucket_uri)
        if not self.verify_bucket_exists():
            raise PublishError(
                's3 bucket "%s" does not exist, please create it first'
                % bucket_uri
            )

        local = self.list_local()
        remote = self.list_remote()
        diff = self.compute_diff(local, remote)

        for f in diff['add']:
            yield 'adding %s' % f
            self.add(f)

        for f in diff['update']:
            yield 'updating %s' % f
            self.update(f)

        for f in diff['delete']:
            yield 'deleting %s' % f
        self.delete_batch(diff['delete'])

        if server_info:
            distribution_id = server_info.extra.get("cloudfront")
        else:
            distribution_id = None

        for message in self.invalidate_cloudfront(distribution_id):
            yield message


def posixify(path):
    """ Ensure that a filepath is slash-delimited, posix-style. """
    return posixpath.join(*split_path(path))


def split_path(path):
    """ Split a path into its components according to the local OS's rules. """
    parts = []
    split = os.path.split(path)
    last_split = ""
    while split[0] != last_split:
        parts.insert(0, split[1])
        last_split = split[0]
        split = os.path.split(split[0])
    if len(split[0]) > 0:
        parts.insert(0, split[0])
    return parts
