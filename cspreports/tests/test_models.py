"""Test for `cspreports.models`."""
import json

from django.test import SimpleTestCase

from cspreports.models import CSPReport


class TestFromMessage(SimpleTestCase):
    """Test `CSPReport.from_message` method."""

    def test_invalid_json(self):
        # Test report which is not a valid JSON.
        report = CSPReport.from_message('NOT_A_JSON')

        self.assertFalse(report.is_valid)
        self.assertEqual(report.json, 'NOT_A_JSON')
        self.assertIsNone(report.document_uri)

    def test_invalid_report(self):
        # Test report which is only a valid JSON.
        report = CSPReport.from_message('{}')

        self.assertFalse(report.is_valid)
        self.assertEqual(report.json, '{}')
        self.assertIsNone(report.document_uri)

    def test_empty_csp_report(self):
        # Test JSON with empty 'csp-report' object.
        report = CSPReport.from_message("{'csp-report': {}}")

        self.assertFalse(report.is_valid)
        self.assertEqual(report.json, "{'csp-report': {}}")
        self.assertIsNone(report.document_uri)

    def test_partial_csp_report(self):
        # Test partial, but invalid CSP report
        data = {'csp-report': {'blocked-uri': 'self', 'violated-directive': 'inline script base restriction'}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertFalse(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertIsNone(report.document_uri)
        self.assertEqual(report.blocked_uri, 'self')
        self.assertEqual(report.violated_directive, 'inline script base restriction')

    def test_valid_csp_1(self):
        # Test valid CSP report according to CSP 1.0
        data = {'csp-report': {'document-uri': 'http://protected.example.cz/',
                               'referrer': 'http://referrer.example.cz/',
                               'blocked-uri': 'http://dangerous.example.cz/',
                               'violated-directive': 'Very protective directive.',
                               'original-policy': 'Nothing is allowed.'}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertTrue(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertIsNone(report.effective_directive)

    def test_valid_csp_2_plus(self):
        # Test valid CSP report according to CSP level >= 2.0
        data = {'csp-report': {'document-uri': 'http://protected.example.cz/',
                               'referrer': 'http://referrer.example.cz/',
                               'blocked-uri': 'http://dangerous.example.cz/',
                               'violated-directive': 'Very protective directive.',
                               'original-policy': 'Nothing is allowed.',
                               'source-file': 'nasty-script.js'}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertTrue(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertEqual(report.source_file, 'nasty-script.js')
        self.assertIsNone(report.effective_directive)

    def test_valid_line_number(self):
        # Test valid line number is extracted.
        data = {'csp-report': {'document-uri': 'http://protected.example.cz/',
                               'referrer': 'http://referrer.example.cz/',
                               'blocked-uri': 'http://dangerous.example.cz/',
                               'violated-directive': 'Very protective directive.',
                               'original-policy': 'Nothing is allowed.',
                               'line-number': 666}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertTrue(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertEqual(report.line_number, 666)

    def test_invalid_line_number(self):
        # Test invalid line number is ignored.
        data = {'csp-report': {'document-uri': 'http://protected.example.cz/',
                               'referrer': 'http://referrer.example.cz/',
                               'blocked-uri': 'http://dangerous.example.cz/',
                               'violated-directive': 'Very protective directive.',
                               'original-policy': 'Nothing is allowed.',
                               'line-number': -666}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertTrue(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertIsNone(report.line_number)

    def test_valid_disposition(self):
        # Test valid disposition is extracted.
        data = {'csp-report': {'document-uri': 'http://protected.example.cz/',
                               'referrer': 'http://referrer.example.cz/',
                               'blocked-uri': 'http://dangerous.example.cz/',
                               'violated-directive': 'Very protective directive.',
                               'original-policy': 'Nothing is allowed.',
                               'disposition': 'report'}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertTrue(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertEqual(report.disposition, 'report')

    def test_invalid_disposition(self):
        # Test invalid disposition is ignored.
        data = {'csp-report': {'document-uri': 'http://protected.example.cz/',
                               'referrer': 'http://referrer.example.cz/',
                               'blocked-uri': 'http://dangerous.example.cz/',
                               'violated-directive': 'Very protective directive.',
                               'original-policy': 'Nothing is allowed.',
                               'disposition': 'INVALID'}}
        message = json.dumps(data)
        report = CSPReport.from_message(message)

        self.assertTrue(report.is_valid)
        self.assertEqual(report.json, message)
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertIsNone(report.disposition)
