"""Test commands."""
from datetime import datetime

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from mock import patch
from six import StringIO

from cspreports.management.commands.clean_cspreports import get_limit
from cspreports.models import CSPReport


class TestGetLimit(SimpleTestCase):
    """Test `get_limit` function."""

    def test_none_aware(self):
        with self.settings(USE_TZ=True, TIME_ZONE='UTC'):
            mock_now = datetime(2016, 4, 27, 12, 34, tzinfo=timezone.utc)
            with patch('cspreports.management.commands.clean_cspreports.now', return_value=mock_now):
                self.assertEqual(get_limit(None), datetime(2016, 4, 20, tzinfo=timezone.utc))

    def test_none_naive(self):
        with self.settings(USE_TZ=False):
            mock_now = datetime(2016, 4, 27, 12, 34)
            with patch('cspreports.management.commands.clean_cspreports.now', return_value=mock_now):
                self.assertEqual(get_limit(None), datetime(2016, 4, 20))

    def test_input_aware(self):
        with self.settings(USE_TZ=True, TIME_ZONE='Europe/Prague'):
            self.assertEqual(get_limit('2016-05-25'), timezone.make_aware(datetime(2016, 5, 25)))

    def test_input_naive(self):
        with self.settings(USE_TZ=False):
            self.assertEqual(get_limit('2016-05-25'), datetime(2016, 5, 25))

    def test_invalid_date(self):
        with self.assertRaisesMessage(ValueError, 'Limit is not a valid date:'):
            get_limit('2016-13-25')

    def test_invalid_input(self):
        with self.assertRaisesMessage(ValueError, 'Limit is not a valid date:'):
            get_limit('INVALID')


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

    @override_settings(USE_TZ=True)
    def test_clean(self):
        # Test reports are cleaned correctly
        self.create_cspreport(datetime(2016, 4, 19, 23, 59, 59, tzinfo=timezone.utc))
        self.create_cspreport(datetime(2016, 4, 20, 0, 0, 0, tzinfo=timezone.utc))
        mock_now = datetime(2016, 4, 27, 12, 34, tzinfo=timezone.utc)
        with patch('cspreports.management.commands.clean_cspreports.localtime', return_value=mock_now):
            call_command('clean_cspreports')

        self.assertQuerysetEqual(CSPReport.objects.values_list('created'),
                                 [(datetime(2016, 4, 20, 0, 0, 0, tzinfo=timezone.utc), )],
                                 transform=tuple)

    def test_invalid(self):
        # Test invalid limit input
        with self.assertRaisesMessage(CommandError, 'Limit is not a valid date:'):
            call_command('clean_cspreports', 'JUNK')
