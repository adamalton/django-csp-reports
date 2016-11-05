#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

PACKAGES = find_packages()

EXTRAS = {
    "test": ["mock"],
}

setup(
    name='django-csp-reports',
    version='1.1',
    description=(
        "A Django app for handling reports from web browsers of violations of your website's "
        "content security policy."
    ),
    author='Adam Alton',
    author_email='adamalton@gmail.com',
    url='https://github.com/adamalton/django-csp-reports',
    download_url='https://github.com/adamalton/django-csp-reports/tarball/1.1',
    packages=PACKAGES,
    include_package_data=True,
    # dependencies
    extras_require=EXTRAS,
    tests_require=EXTRAS['test'],
    keywords=['django', 'csp', 'content security policy'],
    classifiers=['License :: OSI Approved :: MIT License', 'Framework :: Django']
    )
