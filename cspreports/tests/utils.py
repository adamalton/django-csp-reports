"""Test utilities."""
from __future__ import unicode_literals

from cspreports.models import CSPReport


def create_csp_report(created, **kwargs):
    """Create and return a CSP report with a custom created timestamp."""
    # Since the `created` is filled on save, we have to override it manually.
    report = CSPReport.objects.create(**kwargs)
    report.created = created
    report.save()
    return report
