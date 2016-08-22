import os
import posixpath
import ntpath

from unittest import TestCase

import lektor_s3

class MockS3Object(object):
    def __init__(self, key):
        self.key = key


class TestComputeWindowsDiff(TestCase):
    def setUp(self):
        self.old_path = os.path
        os.path = ntpath

        self.old_different = lektor_s3.S3Publisher.different
        def monkeypatched_different(self, *args, **kwargs):
            return False
        lektor_s3.S3Publisher.different = monkeypatched_different

    def tearDown(self):
        os.path = self.old_path
        lektor_s3.S3Publisher.different = self.old_different

    def test_compute_diff(self):
        publisher = lektor_s3.S3Publisher("", "")
        publisher.key_prefix = "/keyprefix/"

        local = [
            r"dir\present_on_both.txt",
            r"dir\missing_remotely.txt",
            r"dir\subdir\file.txt",
            r"toplevel.txt",
        ]
        remote = {
            MockS3Object("/keyprefix/dir/present_on_both.txt"),
            MockS3Object("/keyprefix/dir/missing_locally.txt"),
            MockS3Object("/keyprefix/toplevel.txt"),
            MockS3Object("/keyprefix/dir/subdir/file.txt"),
        }
        have = publisher.compute_diff(local, remote)
        want = {
            'add': [r'dir\missing_remotely.txt'],
            'update': [],
            'delete': ['/keyprefix/dir/missing_locally.txt'],
        }
        self.assertEqual(have, want)


class TestComputePosixDiff(TestCase):
    def setUp(self):
        self.old_path = os.path
        os.path = posixpath

        self.old_different = lektor_s3.S3Publisher.different
        def monkeypatched_different(self, *args, **kwargs):
            return False
        lektor_s3.S3Publisher.different = monkeypatched_different

    def tearDown(self):
        os.path = self.old_path
        lektor_s3.S3Publisher.different = self.old_different

    def test_compute_diff(self):
        publisher = lektor_s3.S3Publisher("", "")
        publisher.key_prefix = "/keyprefix/"

        local = [
            "dir/present_on_both.txt",
            "dir/missing_remotely.txt",
            "dir/subdir/file.txt",
            "toplevel.txt",
        ]
        remote = {
            MockS3Object("/keyprefix/dir/present_on_both.txt"),
            MockS3Object("/keyprefix/dir/missing_locally.txt"),
            MockS3Object("/keyprefix/toplevel.txt"),
            MockS3Object("/keyprefix/dir/subdir/file.txt"),
        }
        have = publisher.compute_diff(local, remote)
        want = {
            'add': ['dir/missing_remotely.txt'],
            'update': [],
            'delete': ['/keyprefix/dir/missing_locally.txt'],
        }
        self.assertEqual(have, want)
