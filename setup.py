#!/usr/bin/env python
from setuptools import find_packages, setup
import os

PACKAGES = find_packages()
REQUIREMENTS = ['django >=2.2,<5.0']
TEST_REQUIREMENTS = ['coverage']
EXTRAS_REQUIRE = {
    'quality': ['isort', 'flake8'],
    'test': TEST_REQUIREMENTS,
}
CLASSIFIERS = ['License :: OSI Approved :: MIT License',
               'Framework :: Django',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3 :: Only',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7',
               'Programming Language :: Python :: 3.8',
               'Programming Language :: Python :: 3.9',
               'Programming Language :: Python :: 3.10',
               'Programming Language :: Python :: 3.11']


DESCRIPTION = (
    "A Django app for handling reports from web browsers of violations of your website's "
    "HTTP Content Security Policy."
)
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

setup(
    name='django-csp-reports',
    version="{{VERSION_PLACEHOLDER}}",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author='Adam Alton',
    author_email='adamalton@gmail.com',
    url='https://github.com/adamalton/django-csp-reports',
    packages=PACKAGES,
    include_package_data=True,
    python_requires='>=3.4',
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    test_suite='runtests.runtests',
    keywords=['django', 'csp', 'content security policy'],
    classifiers=CLASSIFIERS,
)
