"""Test commands."""
from __future__ import unicode_literals

from datetime import datetime

from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from mock import patch
from six import StringIO

from cspreports.models import CSPReport


class TestCleanCspreports(TestCase):
    """Test `clean_cspreports` command."""

    def create_cspreport(self, created):
        report = CSPReport.objects.create()
        report.created = created
        report.save()
        return report

    def test_empty(self):
        # Test case when there's nothing to clean
        call_command('clean_cspreports')

    def test_verbose(self):
        # Test verbose prints message
        buff = StringIO()
        call_command('clean_cspreports', verbosity=2, stdout=buff)
        self.assertIn('Deleted all reports ', buff.getvalue())

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Prague')
    def test_clean(self):
        # Test reports are cleaned correctly
        self.create_cspreport(datetime(2016, 4, 19, 21, 59, 59, tzinfo=timezone.utc))
        self.create_cspreport(datetime(2016, 4, 19, 22, 0, 0, tzinfo=timezone.utc))
        mock_now = datetime(2016, 4, 27, 0, 34, tzinfo=timezone.utc)
        with patch('cspreports.utils.now', return_value=mock_now):
            call_command('clean_cspreports')

        self.assertQuerysetEqual(CSPReport.objects.values_list('created'),
                                 [(datetime(2016, 4, 19, 22, 0, 0, tzinfo=timezone.utc), )],
                                 transform=tuple)

    def test_invalid(self):
        # Test invalid limit input
        with self.assertRaisesMessage(CommandError, "'JUNK' is not a valid date."):
            call_command('clean_cspreports', 'JUNK')
