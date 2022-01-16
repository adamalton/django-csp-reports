"""Command to clean old CSP reports."""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import force_str

from cspreports.models import CSPReport
from cspreports.utils import get_midnight, parse_date_input

DEFAULT_OFFSET = 7


class Command(BaseCommand):
    help = "Delete old CSP reports."

    def add_arguments(self, parser):
        """Parse command arguments."""
        parser.add_argument(
            'limit', nargs='?',
            help="The date until which the reports be deleted. By defalt {} days ago.".format(DEFAULT_OFFSET))

    def handle(self, **options):
        verbosity = options['verbosity']

        limit = options['limit']
        if limit:
            try:
                limit = parse_date_input(limit)
            except ValueError as err:
                raise CommandError(force_str(err))
        else:
            limit = get_midnight() - timedelta(days=DEFAULT_OFFSET)

        CSPReport.objects.filter(created__lt=limit).delete()
        if verbosity >= 2:
            self.stdout.write("Deleted all reports created before {}.".format(limit))
