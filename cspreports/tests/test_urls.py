"""Test for `cspreports.urls`."""

from django.test import SimpleTestCase
from django.urls import include


class TestCSPReportsURLs(SimpleTestCase):
    """Basic tests of CSP reports urls."""

    def test_nice_report_empty(self):
        self.assertTrue(len(include("cspreports.urls")) > 0)
