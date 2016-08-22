# Change Log

## [0.3.1] - 2016-08-22
- Fix to allow uploading from a Windows environment correctly. Before
  this revision, the local filepaths were assumed to be POSIX
  paths. See https://github.com/spenczar/lektor-s3/issues/10.

## [0.3.0] - 2016-05-22
- Automatically invalidate CloudWatch cache if the user provides
  CloudFront distribution ID.

## [0.2.3] - 2016-01-26
- Fix to support Lektor when it passes new keyword arguments through the
  deploy command. This fixes #3 and resolves any future API-breaking changes.

## [0.2.2] - 2016-01-03
- Fix missing import of PublishError

## [0.2.1] - 2015-12-22
- Update to newer Lektor API for registering a publisher plugin

## [0.2] - 2015-12-21
Initial release
