#!/usr/bin/env python
from setuptools import find_packages, setup

PACKAGES = find_packages()
REQUIREMENTS = ['django >=1.8,<2.3', 'six']
TEST_REQUIREMENTS = ['mock', 'coverage']
EXTRAS_REQUIRE = {
    'quality': ['isort', 'flake8'],
    'test': TEST_REQUIREMENTS,
}
CLASSIFIERS = ['License :: OSI Approved :: MIT License',
               'Framework :: Django',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6']


DESCRIPTION = (
    "A Django app for handling reports from web browsers of violations of your website's "
    "HTTP Content Security Policy."
)

setup(
    name='django-csp-reports',
    version='1.3',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author='Adam Alton',
    author_email='adamalton@gmail.com',
    url='https://github.com/adamalton/django-csp-reports',
    download_url='https://github.com/adamalton/django-csp-reports/tarball/1.3',
    packages=PACKAGES,
    include_package_data=True,
    python_requires='>=2.7',
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    test_suite='runtests.runtests',
    keywords=['django', 'csp', 'content security policy'],
    classifiers=CLASSIFIERS,
)
