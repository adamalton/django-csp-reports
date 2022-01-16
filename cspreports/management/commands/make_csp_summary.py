"""Print summary of CSP reports."""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import force_str

from cspreports.summary import DEFAULT_TOP, collect
from cspreports.utils import get_midnight, parse_date_input


def _parse_date_input(date_input, default_offset=0):
    """Parses a date input."""
    if date_input:
        try:
            return parse_date_input(date_input)
        except ValueError as err:
            raise CommandError(force_str(err))
    else:
        return get_midnight() - timedelta(days=default_offset)


class Command(BaseCommand):
    help = "Print summary of CSP reports."

    def add_arguments(self, parser):
        """Parse command arguments."""
        parser.add_argument(
            '--since',
            help="The start date of summary. By default yesterday.")
        parser.add_argument(
            '--to',
            help="The end date of summary. By default yesterday.")
        parser.add_argument(
            '--top', type=int, default=DEFAULT_TOP,
            help="Specifies the size of each section. By default %(default)s.")

    def handle(self, **options):
        since = _parse_date_input(options['since'], 1)
        to = _parse_date_input(options['to'], 1) + timedelta(days=1)
        top = options['top']

        summary = collect(since, to, top)
        self.stdout.write(summary.render())
