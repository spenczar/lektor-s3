import os
import posixpath, ntpath

from unittest import TestCase
import lektor_s3


class TestPosixPaths(TestCase):
    def setUp(self):
        self.old_path = os.path
        os.path = posixpath

    def tearDown(self):
        os.path = self.old_path

    def test_split_abspath(self):
        p = "/some/posixy/path"
        have = lektor_s3.split_path(p)
        self.assertEqual(have, ['/', 'some', 'posixy', 'path'])


    def test_split_abspath_trailing_slash(self):
        p = "/some/posixy/path/"
        have = lektor_s3.split_path(p)
        self.assertEqual(have, ['/', 'some', 'posixy', 'path', ''])

    def test_split_relpath(self):
        p = "some/posixy/path"
        have = lektor_s3.split_path(p)
        self.assertEqual(have, ['some', 'posixy', 'path'])

    def test_posixify(self):
        p = "/some/posixy/path"
        have = lektor_s3.posixify(p)
        self.assertEqual(have, p)

    def test_posixify_with_backlashes(self):
        p = r'some/posixy/path/contains\backslash/inthemiddle'
        have = lektor_s3.posixify(p)
        want = r'some/posixy/path/contains\backslash/inthemiddle'
        self.assertEqual(have, want)


class TestWindowsPaths(TestCase):
    def setUp(self):
        self.old_path = os.path
        os.path = ntpath

    def tearDown(self):
        os.path = self.old_path

    def test_split_abspath(self):
        p = r"c:\\some\windowsy\path"
        have = lektor_s3.split_path(p)
        self.assertEqual(have, [r'c:\\', 'some', 'windowsy', 'path'])

    def test_split_abspath_trailing_slash(self):
        p = r'c:\\some\windowsy\path\\'
        have = lektor_s3.split_path(p)
        self.assertEqual(have, [r'c:\\', 'some', 'windowsy', 'path', ''])

    def test_split_relpath(self):
        p = r"some\windowsy\path"
        have = lektor_s3.split_path(p)
        self.assertEqual(have, ['some', 'windowsy', 'path'])

    def test_posixify(self):
        p = r'some\windowsy\path'
        have = lektor_s3.posixify(p)
        want = "some/windowsy/path"
        self.assertEqual(have, want)

    def test_posixify_with_slashes(self):
        p = r'some\windowsy\path\contains/slash\inthemiddle'
        have = lektor_s3.posixify(p)
        want = "some/windowsy/path/contains/slash/inthemiddle"
        self.assertEqual(have, want)
