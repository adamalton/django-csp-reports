from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.test.signals import setting_changed

from cspreports.models import get_report_model
from cspreports.conf import app_settings
from cspreports.tests.models import CustomCSPReport


class TestGetReportModelModel(TestCase):
    @override_settings(CSP_REPORTS_MODEL="tests.CustomCSPReport")
    def test_custom_get_report_model(self):
        """Test get_report_model with a custom report model"""
        self.assertIs(get_report_model(), CustomCSPReport)

    @override_settings(CSP_REPORTS_MODEL="tests.CustomCSPReport")
    def test_custom_get_report_model_string(self):
        """Test model string with a custom report model"""
        self.assertEqual(app_settings.CSP_REPORT_MODEL, "tests.CustomCSPReport")

    @override_settings()
    def test_standard_get_report_model(self):
        """Test get_report_model with no CSP_REPORTS_MODEL"""
        del settings.CSP_REPORTS_MODEL
        from cspreports.models import CSPReport

        self.assertIs(get_report_model(), CSPReport)

    @override_settings()
    def test_standard_get_report_model_string(self):
        """Test model string with no CSP_REPORTS_MODEL"""
        del settings.CSP_REPORTS_MODEL
        self.assertEqual(app_settings.CSP_REPORT_MODEL, "cspreports.CSPReport")

    @override_settings(CSP_REPORTS_MODEL="tests.UnknownModel")
    def test_unknown_get_report_model(self):
        """Test get_report_model with an unknown model"""
        with self.assertRaises(ImproperlyConfigured):
            get_report_model()

    @override_settings(CSP_REPORTS_MODEL="invalid-string")
    def test_invalid_get_report_model(self):
        """Test get_report_model with an invalid model string"""
        with self.assertRaises(ImproperlyConfigured):
            get_report_model()
