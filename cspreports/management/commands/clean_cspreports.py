"""Command to clean old CSP reports."""
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date
from django.utils.encoding import force_text
from django.utils.timezone import localtime, make_aware, now

from cspreports.models import CSPReport

DEFAULT_OFFSET = 7


def get_limit(value):
    """Returns limit datetime based on the user's input.

    @param value: User's input or None
    @type value: str
    @raise ValueError: If the input is not valid.
    """
    limit = None
    if value:
        try:
            limit = parse_date(value)
        except ValueError:
            limit = None
        if limit is None:
            raise ValueError("Limit is not a valid date: '{}'.".format(value))
        limit = datetime(limit.year, limit.month, limit.day)
        if settings.USE_TZ:
            limit = make_aware(limit)
        return limit
    else:
        limit = now()
        if settings.USE_TZ:
            limit = localtime(limit)
        return limit.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=DEFAULT_OFFSET)


class Command(BaseCommand):
    help = "Delete old CSP reports."

    def add_arguments(self, parser):
        """Parse command arguments."""
        parser.add_argument(
            'limit', nargs='?',
            help="The date until which the reports be deleted. By defalt {} days ago.".format(DEFAULT_OFFSET))

    def handle(self, **options):
        verbosity = options['verbosity']
        try:
            limit = get_limit(options['limit'])
        except ValueError as err:
            raise CommandError(force_text(err))

        CSPReport.objects.filter(created__lt=limit).delete()
        if verbosity >= 2:
            self.stdout.write("Deleted all reports created before {}.".format(limit))
