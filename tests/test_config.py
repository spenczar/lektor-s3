import ConfigParser

from unittest import TestCase

import lektor_s3


class TestConfigureHeaders(TestCase):
    def setUp(self):
        self.old_get_config = lektor_s3.S3Publisher.get_config
        def monkeypatched_get_config(self, *args, **kwargs):
            config = ConfigParser.RawConfigParser(defaults={'CacheControl': 'public,max-age=3600'})
            config.add_section('fonts')
            config.set('fonts', 'ContentType', 'application/font-woff2')
            config.set('fonts', 'extensions', 'woff2')
            config.add_section('media')
            config.set('media', 'CacheControl', 'public,max-age=259200')
            config.set('media', 'extensions', 'jpg,jpeg,png,mp4')
            config.add_section('static files')
            config.set('static files', 'CacheControl', 'public,max-age=31536000')
            config.set('static files', 'match', '.(css|js|woff|woff2)$')
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
