"""Collect summary of CSP reports."""
from operator import attrgetter
from urllib.parse import urlsplit, urlunsplit

from django.template.loader import get_template

from cspreports.models import CSPReport

DEFAULT_TOP = 10


def get_root_uri(uri):
    """Return root URI - strip query and fragment."""
    chunks = urlsplit(uri)
    return urlunsplit((chunks.scheme, chunks.netloc, chunks.path, '', ''))


class ViolationInfo:
    """Container for violation details.

    @ivar root_uri: A violation root URI.
    @ivar count: A number of violations related to the root URI.
    @ivar examples: List of violation examples.
    @ivar top: Maximal number of examples.
    """

    def __init__(self, root_uri, top=DEFAULT_TOP):
        self.root_uri = root_uri
        self.count = 0
        self.examples = []
        self.top = top

    def append(self, report):
        """Append a new CSP report."""
        assert report not in self.examples
        self.count += 1
        if len(self.examples) < self.top:
            self.examples.append(report)


class CspReportSummary:
    """CSP report summary.

    @ivar since: Date and time of the summary start
    @ivar to: Date and time of the summary end
    @ivar top: Size of each section

    @ivar total_count: Total number of CSP reports
    @ivar valid_count: Total number of valid reports
    @ivar invalid_count: Total number of invalid reports

    @ivar sources: List of top sources of violations ordered by descending count
    @type sources: List[ViolationInfo]
    @ivar blocks: List of top blocked URIs ordered by descending count
    @type blocks: List[ViolationInfo]
    @ivar invalid_reports: Examples of invalid CSP reports
    """

    def __init__(self, since, to, top=DEFAULT_TOP):
        self.since = since
        self.to = to
        self.top = top

        self.total_count = 0
        self.valid_count = 0
        self.sources = []
        self.blocks = []
        self.invalid_count = 0
        self.invalid_reports = ()

    def render(self):
        """Render the summary."""
        template = get_template('cspreports/summary.txt')
        return template.render(self.__dict__)


def collect(since, to, top=DEFAULT_TOP):
    """Collect the CSP report.

    @returntype: CspReportSummary
    """
    summary = CspReportSummary(since, to, top=top)
    queryset = CSPReport.objects.filter(created__range=(since, to))
    valid_queryset = queryset.filter(is_valid=True)
    invalid_queryset = queryset.filter(is_valid=False)

    summary.total_count = queryset.count()
    summary.valid_count = valid_queryset.count()

    # Collect sources
    sources = {}
    for report in valid_queryset:
        root_uri = get_root_uri(report.document_uri)
        info = sources.setdefault(root_uri, ViolationInfo(root_uri))
        info.append(report)
    summary.sources = sorted(sources.values(), key=attrgetter('count'), reverse=True)[:top]

    # Collect blocks
    blocks = {}
    for report in valid_queryset:
        root_uri = get_root_uri(report.blocked_uri)
        info = blocks.setdefault(root_uri, ViolationInfo(root_uri))
        info.append(report)
    summary.blocks = sorted(blocks.values(), key=attrgetter('count'), reverse=True)[:top]

    # Collect invalid reports
    summary.invalid_count = invalid_queryset.count()
    summary.invalid_reports = tuple(invalid_queryset[:top])

    return summary
