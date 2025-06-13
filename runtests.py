#!/usr/bin/env python
"""Script to run tests.

This file is required to run Django tests in tox.
Based on http://joebergantine.com/articles/reusable-django-application-travis-tox/
"""

import os
import sys
import django

from django.conf import settings
from django.test.utils import get_runner


def runtests():
    os.environ["DJANGO_SETTINGS_MODULE"] = "cspreports.tests.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["cspreports"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    runtests()
