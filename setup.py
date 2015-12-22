from setuptools import setup

setup(
    name='lektor-s3',
    version='0.1',
    author=u'Spencer Nelson',
    author_email='s@spenczar.com',
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
