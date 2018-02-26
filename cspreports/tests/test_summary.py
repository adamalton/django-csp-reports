"""Test `summary` module."""
from __future__ import unicode_literals

from datetime import datetime

from django.test import SimpleTestCase, TestCase
from mock import sentinel
from six import assertCountEqual

from cspreports.models import CSPReport
from cspreports.summary import CspReportSummary, ViolationInfo, collect, get_root_uri

from .utils import create_csp_report


class TestGetRootUri(SimpleTestCase):
    """Test `get_root_uri` function."""

    def test_root_uri(self):
        self.assertEqual(get_root_uri(''), '')
        self.assertEqual(get_root_uri('self'), 'self')
        self.assertEqual(get_root_uri('http://example.cz/'), 'http://example.cz/')
        self.assertEqual(get_root_uri('http://example.cz/path/'), 'http://example.cz/path/')
        self.assertEqual(get_root_uri('http://example.cz/path/?query=value'), 'http://example.cz/path/')
        self.assertEqual(get_root_uri('http://example.cz/path/#fragment'), 'http://example.cz/path/')


class TestViolationInfo(SimpleTestCase):
    """Test `ViolationInfo` class."""

    def test_empty(self):
        info = ViolationInfo(sentinel.root_uri)

        self.assertEqual(info.root_uri, sentinel.root_uri)
        self.assertEqual(info.count, 0)
        self.assertEqual(info.examples, [])

    def test_append(self):
        info = ViolationInfo(sentinel.root_uri)
        info.append(sentinel.report)

        self.assertEqual(info.count, 1)
        self.assertEqual(info.examples, [sentinel.report])

    def test_append_top(self):
        # Test appending over the limit
        info = ViolationInfo(sentinel.root_uri, top=2)
        info.append(sentinel.report_1)
        info.append(sentinel.report_2)

        info.append(sentinel.report_over)

        self.assertEqual(info.count, 3)
        self.assertEqual(info.examples, [sentinel.report_1, sentinel.report_2])


class TestCspReportSummary(SimpleTestCase):
    """Test `CspReportSummary` class."""

    def test_render_empty(self):
        summary = CspReportSummary(sentinel.since, sentinel.to)

        output = summary.render()

        self.assertIn('CSP report summary', output)

    def test_render_reports(self):
        summary = CspReportSummary(sentinel.since, sentinel.to)
        summary.total_count = 42
        summary.valid_count = 32
        summary.invalid_count = 10
        violation = ViolationInfo('http://example.cz/')
        violation.append(CSPReport())
        summary.sources = [violation]
        summary.blocks = [violation]

        output = summary.render()

        self.assertIn('CSP report summary', output)
        self.assertIn('Violation sources', output)
        self.assertIn('Blocked URIs', output)


class TestCollect(TestCase):
    """Test `collect` function."""

    def test_no_reports(self):
        summary = collect(datetime(1970, 1, 1), datetime(1970, 12, 31))

        self.assertEqual(summary.total_count, 0)
        self.assertEqual(summary.valid_count, 0)
        assertCountEqual(self, summary.sources, ())
        assertCountEqual(self, summary.blocks, ())
        self.assertEqual(summary.invalid_count, 0)
        assertCountEqual(self, summary.invalid_reports, ())

    def test_invalid_reports(self):
        report1 = create_csp_report(datetime(1970, 1, 1, 12))
        report2 = create_csp_report(datetime(1970, 1, 1, 12))
        summary = collect(datetime(1970, 1, 1), datetime(1970, 12, 31))

        self.assertEqual(summary.total_count, 2)
        self.assertEqual(summary.valid_count, 0)
        assertCountEqual(self, summary.sources, ())
        assertCountEqual(self, summary.blocks, ())
        self.assertEqual(summary.invalid_count, 2)
        assertCountEqual(self, summary.invalid_reports, (report1, report2))

    def test_valid_reports(self):
        report1 = create_csp_report(datetime(1970, 1, 1, 12), is_valid=True, document_uri='http://example.cz/',
                                    blocked_uri='http://example.evil/')
        report2 = create_csp_report(datetime(1970, 1, 1, 12), is_valid=True,
                                    document_uri='http://example.cz/?key=value',
                                    blocked_uri='http://example.evil/')
        summary = collect(datetime(1970, 1, 1), datetime(1970, 12, 31))

        self.assertEqual(summary.total_count, 2)
        self.assertEqual(summary.valid_count, 2)
        # Check sources
        self.assertEqual(len(summary.sources), 1)
        source = summary.sources[0]
        self.assertEqual(source.root_uri, 'http://example.cz/')
        self.assertEqual(source.count, 2)
        assertCountEqual(self, source.examples, (report1, report2))
        # Check blocks
        self.assertEqual(len(summary.blocks), 1)
        block = summary.blocks[0]
        self.assertEqual(block.root_uri, 'http://example.evil/')
        self.assertEqual(block.count, 2)
        assertCountEqual(self, block.examples, (report1, report2))
        # Check invalid
        self.assertEqual(summary.invalid_count, 0)
        assertCountEqual(self, summary.invalid_reports, ())
