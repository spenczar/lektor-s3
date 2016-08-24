# lektor-s3 #

lektor-s3 makes it easy to deploy your
[Lektor](https://github.com/lektor/lektor) project to an S3 bucket.

## Before you start ##

You're going to be storing your website's data in an S3 bucket. The code
here won't do anything to create or configure that bucket. You'll have to
create the S3 bucket and set it up yourself.

AWS has a [pretty good guide](http://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html)
for how to set up a bucket to host a static website. You'll need to both
create the bucket and set its permissions to allow global read access.
Remember to do this **first** because lektor-s3 won't do it automatically.


## Installation and Usage ##
Install with the usual Lektor toolchain. Within your project, run

```console
lektor plugins add lektor-s3
```

You should see a message saying lektor-s3 has been added to the project.

Next, add an S3 bucket to your project's servers. In your project file
(like `blog.lektorproject`), add the following:

```ini
[servers.s3]
name = S3
enabled = yes
target = s3://<YOUR-BUCKET>
```

For example, if you wanted to deploy to a bucket named 'huntedwumpus',
you'd make that last line

```ini
target = s3://huntedwumpus
```

Now, if you call `lektor deploy s3`, Lektor will upload your built
website to S3 in the bucket you targeted.

## CloudFront ##

Optionally, you can also provide a [CloudFront](https://aws.amazon.com/cloudfront/)
distribution ID. If you do, Lektor will invalidate all objects in that CloudFront
distribution after every deploy.

```ini
cloudfront = <YOUR-DISTRIBUTION-ID>
```

## Credentials ##

You need to prove to S3 that you have permission to upload to the
bucket you've chosen.

lektor-s3 uses boto, which means it will obey
[boto's usual flow for gathering credentials](http://boto3.readthedocs.org/en/latest/guide/configuration.html).

For a refresher, that means you have two options: you can store your
credentials in an INI file at `~/.aws/credentials`, or you can pass
credentials in through the environment variables `AWS_ACCESS_KEY_ID`
and `AWS_SECRET_ACCESS_KEY`.

If you have multiple sets of credentials, you can group them into profiles in
your credentials file and choose the right one using the `AWS_PROFILE`
environment variable. Your `~/.aws/credenials` file might look like this:

```ini
[work]
aws_access_key_id = <...>
aws_secret_access_key = <...>

[personal]
aws_access_key_id = <...>
aws_secret_access_key = <...>
```

And then you can invoke `lektor` with the environment variable:

```console
$ AWS_PROFILE=personal lektor deploy`
```

## Configuration ##

You can specify headers to be attached to particular files when uploading them
to S3. These can be configured in an INI file at `configs/s3.ini` under your
project root.

You can name the sections anything that makes sense to you, but every section
must have either a `match` or an `extensions` item to specify which files the
configuration applies to. If using `match`, you should write this as a regular
expression that will be applied against the filename using the regular
expression's search method. If using `extensions`, write a comma-separated list
of the file extensions to which the configuration applies. Both `match` and
`extensions` may be specified.

The rest of the items in each section should specify one or more headers and
their values. A list of valid headers is defined in the boto documentation as
 [`ALLOWED_UPLOAD_ARGS`](https://boto3.readthedocs.io/en/latest/reference/customizations/s3.html#boto3.s3.transfer.S3Transfer.ALLOWED_UPLOAD_ARGS).

Defaults can be defined via the usual INI file way, in a `[DEFAULTS]` section.

For example, your configuration file might look like this:

```ini
[DEFAULT]
CacheControl = public,max-age=3600

[static files]
match = \.(css|js|woff|woff2)$
CacheControl = public,max-age=31536000

[media]
extensions = jpg,jpeg,png,mp4
CacheControl = public,max-age=259200

[fonts]
extensions = woff2
ContentType = application/font-woff2

[documents]
extensions = html,txt
ContentLanguage = en
```

## Contributing ##

Pull requests are super useful and encouraged! Once accepted, changes
are published using lektor with `lektor dev publish-plugin`.

Run your tests by invoking `python setup.py test`.
