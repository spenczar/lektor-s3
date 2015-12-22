from setuptools import setup

setup(
    name='lektor-s3',
    description='Lektor plugin to support publishing to S3',
    version='0.2.1',
    author=u'Spencer Nelson',
    author_email='s@spenczar.com',
    url='https://github.com/spenczar/lektor-s3',
    license='MIT',
    py_modules=['lektor_s3'],
    entry_points={
        'lektor.plugins': [
            's3 = lektor_s3:S3Plugin',
        ]
    },
    install_requires=[
        'Lektor',
        'boto3>=1.1.4',
    ]
)
