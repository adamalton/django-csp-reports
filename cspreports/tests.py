# STANDARD LIB
from contextlib import nested

# LIBRARIES
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
import mock

# CSP REPORTS
from cspreports import utils


class CSPReportsTest(TestCase):

    def test_custom_handler(self):
        pass


class UtilsTest(TestCase):


    def test_config(self):
        """ Test that the various CSP_REPORTS_X settings correctly control which handlers are called. """
        mock_paths  = [
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

