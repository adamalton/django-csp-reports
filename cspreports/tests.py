# STANDARD LIB
from contextlib import nested

# LIBRARIES
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
import mock

# CSP REPORTS
from cspreports.models import CSPReport
from cspreports import utils


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
        for i in xrange(len(mock_paths)):
            mocks = [mock.patch(path) for path in mock_paths]
            settings_overrides = {
                setting: True if j == i else False
                for j, setting in enumerate(corresponding_settings)
            }
            with override_settings(**settings_overrides):
                with nested(*mocks) as mocked_objects:
                    request = HttpRequest()
                    utils.process_report(request)
                    for k, mocked_object in enumerate(mocked_objects):
                        if k == i:
                            self.assertTrue(mocked_object.called)
                        else:
                            self.assertFalse(mocked_object.called)

    def test_save_report(self):
        """ Test that the `save_report` handler correctly saves to the DB. """
        assert CSPReport.objects.count() == 0  # sanity
        request = HttpRequest()
        request._body = '{"document-uri": "http://example.com/"}'
        utils.save_report(request)
        reports = list(CSPReport.objects.all())
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].json, request.body)

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
            CSP_REPORTS_ADDITIONAL_HANDLERS=["cspreports.tests.my_handler"],
            CSP_REPORTS_EMAIL_ADMINS=False,
            CSP_REPORTS_LOG=False,
            CSP_REPORTS_SAVE=False,
        ):
            utils.process_report(request)
            self.assertTrue(request.my_handler_called)


def my_handler(request):
    # just set an attribute so that we can see that this function has been called
    request.my_handler_called = True
