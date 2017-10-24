#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = '0.1.5'

setup(
    name='UserGrid',
    version='0.1.4',
    description='UserGrid 1.x Client',
    author='Christopher Smith',
    author_email='chris.s@bigmirrorlabs.com',
    packages=find_packages(exclude=['tests']),
    package_dir={
        'usergrid': 'usergrid'
    },
    install_requires=[
        'certifi==2017.7.27.1',
        'chardet==3.0.4',
        'idna==2.6',
        'requests==2.18.4',
        'requests-mock==1.3.0',
        'six==1.11.0',
        'urllib3==1.22'
    ],
    include_package_data=True
)
