#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = '0.1.4'

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
        'requests'
    ],
    include_package_data=True
)
