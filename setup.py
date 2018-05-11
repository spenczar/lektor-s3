from setuptools import setup

with open('README.md', 'rt', encoding='utf8') as readme_file:
    readme = readme_file.read()

setup(
    name='lektor-s3',
    description='Lektor plugin to support publishing to S3',
    long_description=readme,
    long_description_content_type='text/markdown',
    version='0.5.0',
    author='Spencer Nelson',
    author_email='s@spenczar.com',
    url='https://github.com/spenczar/lektor-s3',
    license='MIT',
    platforms='any',
    py_modules=['lektor_s3'],
    entry_points={
        'lektor.plugins': [
            's3 = lektor_s3:S3Plugin',
        ]
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'boto3>=1.1.4',
        's3transfer',
    ],
    install_requires=[
        'Lektor',
        'boto3>=1.1.4',
        's3transfer',
        'inifile',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Lektor',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
