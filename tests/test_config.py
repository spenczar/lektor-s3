from contextlib import contextmanager
import os
import shutil
import tempfile
from unittest import TestCase

import inifile
from lektor.environment import Environment
import lektor_s3


class MockEnvironment(object):
    def __init__(self, root_path):
        self.root_path = root_path

@contextmanager
def TemporaryDirectory():
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        shutil.rmtree(name)


class TestLoadConfig(TestCase):
    def test_no_config_file(self):
        publisher = lektor_s3.S3Publisher(MockEnvironment(""), "")
        self.assertEqual(len(list(publisher.get_config().sections())), 0)

    def test_load_config_file(self):
        with TemporaryDirectory() as tempdir:
            os.mkdir(os.path.join(tempdir, "configs"))
            config = inifile.IniFile(os.path.join(tempdir, "configs", "s3.ini"))
            config["section.key"] = "value"
            config.save()

            publisher = lektor_s3.S3Publisher(MockEnvironment(tempdir), "")
            have = publisher.get_config().section_as_dict("section")
            self.assertEqual(have["key"], "value")


class TestConfigureHeaders(TestCase):
    def setUp(self):
        self.old_get_config = lektor_s3.S3Publisher.get_config
        def monkeypatched_get_config(self, *args, **kwargs):
            config = inifile.IniData(mapping={
                "DEFAULTS.CacheControl": "public,max-age=3600",
                "fonts.ContentType": "application/font-woff2",
                "fonts.extensions": "woff2",
                "media.CacheControl": "public,max-age=259200",
                "media.extensions": "jpg,jpeg,png,mp4",
                "static files.CacheControl": "public,max-age=31536000",
                "static files.match": "\.(css|js|woff|woff2)$",
            })
            return config
        lektor_s3.S3Publisher.get_config = monkeypatched_get_config

    def tearDown(self):
        lektor_s3.S3Publisher.get_config = self.old_get_config

    def test_default(self):
        publisher = lektor_s3.S3Publisher("", "")

        filename = r"index.html"
        have = publisher.create_headers(filename)
        want = {
            'CacheControl': 'public,max-age=3600',
            'ContentType': 'text/html',
        }
        self.assertEqual(have, want)

    def test_match(self):
        publisher = lektor_s3.S3Publisher("", "")

        filename = r"styles.css"
        have = publisher.create_headers(filename)
        want = {
            'CacheControl': 'public,max-age=31536000',
            'ContentType': 'text/css',
        }
        self.assertEqual(have, want)

    def test_extensions(self):
        publisher = lektor_s3.S3Publisher("", "")

        filename = r"image.png"
        have = publisher.create_headers(filename)
        want = {
            'CacheControl': 'public,max-age=259200',
            'ContentType': 'image/png',
        }
        self.assertEqual(have, want)

    def test_multiple_rules(self):
        publisher = lektor_s3.S3Publisher("", "")

        filename = r"font.woff2"
        have = publisher.create_headers(filename)
        want = {
            'CacheControl': 'public,max-age=31536000',
            'ContentType': 'application/font-woff2',
        }
        self.assertEqual(have, want)
