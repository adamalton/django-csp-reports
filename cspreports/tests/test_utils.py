from __future__ import unicode_literals

import json
from datetime import datetime

import mock
from django.http import HttpRequest
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.test.utils import override_settings
from django.utils import timezone
from mock import patch

from cspreports import utils
from cspreports.models import CSPReport
from cspreports.utils import get_midnight, parse_date_input

JSON_CONTENT_TYPE = 'application/json'


class UtilsTest(TestCase):

    def test_config(self):
        """ Test that the various CSP_REPORTS_X settings correctly control which handlers are
            called.
        """
        mock_paths = [
            "cspreports.utils.email_admins",
            "cspreports.utils.save_report",
            "cspreports.utils.log_report",
        ]
        corresponding_settings = [
            "CSP_REPORTS_EMAIL_ADMINS",
            "CSP_REPORTS_SAVE",
            "CSP_REPORTS_LOG",
        ]
        for i in range(len(mock_paths)):
            mocks = [mock.patch(path) for path in mock_paths]
            settings_overrides = {
                setting: True if j == i else False
                for j, setting in enumerate(corresponding_settings)
            }
            with override_settings(**settings_overrides):
                with mocks[0] as mocked_object_0, mocks[1] as mocked_object_1, mocks[2] as mocked_object_2:
                    mocked_objects = [mocked_object_0, mocked_object_1, mocked_object_2]
                    request = HttpRequest()
                    utils.process_report(request)
                    for k, mocked_object in enumerate(mocked_objects):
                        if k == i:
                            self.assertTrue(mocked_object.called)
                        else:
                            self.assertFalse(mocked_object.called)

    @override_settings(CSP_REPORTS_LOG_LEVEL='warning')
    def test_log_report(self):
        """ Test that the `log_report` handler correctly logs at the right level. """
        request = HttpRequest()
        report = '{"document-uri": "http://example.com/"}'
        formatted_report = utils.format_report(report)
        request._body = report
        with mock.patch("cspreports.utils.logger.warning") as warning_mock:
            utils.log_report(request)
            self.assertTrue(warning_mock.called)
            log_message = warning_mock.call_args[0][0] % warning_mock.call_args[0][1:]
            self.assertTrue(formatted_report in log_message)

    def test_email_admins(self):
        """ Test that the `email_admins` handler correctly sends an email. """
        request = HttpRequest()
        report = '{"document-uri": "http://example.com/"}'
        formatted_report = utils.format_report(report)
        request._body = report
        # Note that we are mocking the *Django* mail_admins function here.
        with mock.patch("cspreports.utils.mail_admins") as mock_mail_admins:
            utils.email_admins(request)
            self.assertTrue(mock_mail_admins.called)
            message = mock_mail_admins.call_args[0][1]
            self.assertTrue(formatted_report in message)

    def test_format_report_handles_invalid_json(self):
        """ Test that `format_report` doesn't trip up on invalid JSON.
            Note: this is about not getting a ValueError, rather than any kind of security thing.
        """
        invalid_json = '{"key": undefined_variable, nonsense here}'
        try:
            formatted = utils.format_report(invalid_json)
        except ValueError as e:
            self.fail("format_report did not handle invalid JSON: %s" % e)
        # we expect our invalid JSON to remain in the output, as is
        self.assertTrue(invalid_json in formatted)

    def test_run_additional_handlers(self):
        """ Test that the run_additional_handlers function correctly calls each of the specified custom
            handler functions.
        """
        # utils stores a cache of the handlers (for efficiency, so kill that)
        utils._additional_handlers = None
        request = HttpRequest()
        with override_settings(
            CSP_REPORTS_ADDITIONAL_HANDLERS=["cspreports.tests.test_utils.my_handler"],
            CSP_REPORTS_EMAIL_ADMINS=False,
            CSP_REPORTS_LOG=False,
            CSP_REPORTS_SAVE=False,
        ):
            utils.process_report(request)
            self.assertTrue(request.my_handler_called)

    @override_settings(CSP_REPORTS_FILTER_FUNCTION='cspreports.tests.test_utils.example_filter')
    def test_filter_function(self):
        """ Test that setting CSP_REPORTS_FILTER_FUNCTION allows the given function to filter out
            requests.
        """
        report1 = '{"document-uri": "http://not-included.com/"}'
        report2 = '{"document-uri": "http://included.com/"}'
        request = HttpRequest()
        request._body = report1
        with mock.patch('cspreports.utils.log_report') as log_patch:
            utils.process_report(request)
            self.assertFalse(log_patch.called)
            request._body = report2
            utils.process_report(request)
            self.assertTrue(log_patch.called)


def my_handler(request):
    # just set an attribute so that we can see that this function has been called
    request.my_handler_called = True


def example_filter(request):
    """ Filters out reports with a 'document-uri' not from included.com. """
    report = json.loads(request.body)
    doc_uri = report.get('document-uri', '')
    if doc_uri.startswith('http://included.com'):
        return True
    return False


class TestParseDateInput(SimpleTestCase):
    """Test `parse_date_input` function."""

    def test_aware(self):
        with self.settings(USE_TZ=True, TIME_ZONE='Europe/Prague'):
            self.assertEqual(parse_date_input('2016-05-25'), timezone.make_aware(datetime(2016, 5, 25)))

    def test_naive(self):
        with self.settings(USE_TZ=False):
            self.assertEqual(parse_date_input('2016-05-25'), datetime(2016, 5, 25))

    def test_invalid_date(self):
        with self.assertRaisesMessage(ValueError, 'is not a valid date.'):
            parse_date_input('2016-13-25')

    def test_invalid_input(self):
        with self.assertRaisesMessage(ValueError, 'is not a valid date.'):
            parse_date_input('INVALID')


class TestGetMidnight(SimpleTestCase):
    """Test `get_midnight` function."""

    def test_aware(self):
        with self.settings(USE_TZ=True, TIME_ZONE='Europe/Prague'):
            # 00:05 in CEST is 22:05 day before in UTC
            mock_now = datetime(2016, 4, 26, 22, 5, tzinfo=timezone.utc)
            with patch('cspreports.utils.now', return_value=mock_now):
                self.assertEqual(get_midnight(), datetime(2016, 4, 26, 22, 0, tzinfo=timezone.utc))

    def test_naive(self):
        with self.settings(USE_TZ=False):
            mock_now = datetime(2016, 4, 27, 12, 34)
            with patch('cspreports.utils.now', return_value=mock_now):
                self.assertEqual(get_midnight(), datetime(2016, 4, 27))


class SaveReportTest(TestCase):

    def test_save_report_missing_root_element(self):
        """ Test that the `save_report` handler correctly saves to the DB. """
        assert CSPReport.objects.count() == 0  # sanity
        body = '{"document-uri": "http://example.com/"}'
        request = RequestFactory(HTTP_USER_AGENT='Agent007').post('/dummy/', body, content_type=JSON_CONTENT_TYPE)

        utils.save_report(request)

        reports = CSPReport.objects.all()
        self.assertQuerysetEqual(reports.values_list('user_agent'), [('Agent007', )], transform=tuple)
        report = reports[0]
        self.assertEqual(report.json, body)
        self.assertFalse(report.is_valid)

    def test_save_report_no_agent(self):
        """Test that the `save_report` handler correctly handles missing user agent header."""
        request = RequestFactory().post('/dummy/', '{"document-uri": "http://example.com/"}',
                                        content_type=JSON_CONTENT_TYPE)

        utils.save_report(request)

        reports = CSPReport.objects.all()
        report = reports[0]
        self.assertQuerysetEqual(report.user_agent, '')

    def test_save_report_correct_format_missing_mandatory_fields(self):
        """ Test that the `save_report` saves CSPReport instance even if some required CSP Report fields are missing."""
        assert CSPReport.objects.count() == 0  # sanity
        body = {
            'csp-report': {
                'document-uri': 'http://protected.example.cz/',
                'referrer': '',
                'blocked-uri': '',
                'violated-directive': 'Very protective directive.',
                'original-policy': 'Nothing is allowed.'
            }
        }
        request = RequestFactory(HTTP_USER_AGENT='Agent007').post('/dummy/', json.dumps(body),
                                                                  content_type=JSON_CONTENT_TYPE)
        utils.save_report(request)

        reports = CSPReport.objects.all()
        self.assertQuerysetEqual(reports.values_list('user_agent'), [('Agent007', )], transform=tuple)
        report = reports[0]
        self.assertEqual(report.json, json.dumps(body))
        self.assertTrue(report.is_valid)

    def test_save_report_correct_optional_fields(self):
        """ Test that the `save_report` saves CSPReport instance even if some required CSP Report fields are missing."""
        assert CSPReport.objects.count() == 0  # sanity
        body = {
            'csp-report': {
                'document-uri': 'http://protected.example.cz/',
                'referrer': 'http://referrer.example.cz/',
                'blocked-uri': 'http://dangerous.example.cz/',
                'violated-directive': 'Very protective directive.',
                'original-policy': 'Nothing is allowed.',
                'source-file': 'nasty-script.js',
                'status-code': 0,
                'line-number': '36',
                'column-number': 32,
            }
        }
        request = RequestFactory(HTTP_USER_AGENT='Agent007').post('/dummy/', json.dumps(body),
                                                                  content_type=JSON_CONTENT_TYPE)
        utils.save_report(request)

        reports = CSPReport.objects.all()
        report = reports[0]
        self.assertEqual(report.json, json.dumps(body))
        self.assertEqual(report.user_agent, 'Agent007')
        self.assertEqual(report.document_uri, 'http://protected.example.cz/')
        self.assertEqual(report.referrer, 'http://referrer.example.cz/')
        self.assertEqual(report.blocked_uri, 'http://dangerous.example.cz/')
        self.assertEqual(report.violated_directive, 'Very protective directive.')
        self.assertEqual(report.original_policy, 'Nothing is allowed.')
        self.assertEqual(report.source_file, 'nasty-script.js')
        self.assertEqual(report.status_code, 0)
        self.assertEqual(report.line_number, 36)
        self.assertEqual(report.column_number, 32)
        self.assertTrue(report.is_valid)
