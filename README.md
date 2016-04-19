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

## Contributing ##

Pull requests are super useful and encouraged! Once accepted, changes
are published using lektor with `lektor dev publish-plugin`.
