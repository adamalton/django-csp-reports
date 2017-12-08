#!/usr/bin/env python
from setuptools import find_packages, setup

PACKAGES = find_packages()
REQUIREMENTS = ['django >=1.8,<1.11.99']
TEST_REQUIREMENTS = ['mock']

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
    python_requires='>=2.7,<3',
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    test_suite='runtests.runtests',
    keywords=['django', 'csp', 'content security policy'],
    classifiers=['License :: OSI Approved :: MIT License', 'Framework :: Django'],
)
