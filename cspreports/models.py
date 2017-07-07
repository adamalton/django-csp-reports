# STANDARD LIB
import json

# LIBRARIES
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe

DISPOSITIONS = (
    ('enforce', 'enforce'),
    ('report', 'report'),
)


class CSPReport(models.Model):
    """Represents a CSP violation report.

    @ivar created: Date and time of report creation.
    @ivar modified: Date and time of last modification.
    @ivar json: Raw CSP report
    @ivar is_valid: Whether the CSP report is valid.

    All report fields are NULL is report is invalid.
    Report fields are NULL if the report follows the rules of lower protocol level.

    CSP 1.0 fields:
    @ivar document_uri: The URI of protected resource.
    @ivar referrer: The referrer attribute of the protected resource.
    @ivar blocked_uri: The URI of the resource that was prevented from loading due to the policy violation.
    @ivar violated_directive: The policy directive that was violated.
    @ivar original_policy: The original policy as received by the user-agent.

    CSP 2.0 fields
    @ivar effective_directive: The name of the policy directive that was violated.
    @ivar status_code: The status-code of the HTTP response that contained the protected resource.
    @ivar source_file: The URL of the resource where the violation occurred.
    @ivar line_number: The line number in source-file on which the violation occurred.
    @ivar column_number: The column number in source-file on which the violation occurred.

    CSP 3.0 fields
    @ivar disposition: The disposition of violation's policy.
    """

    class Meta(object):
        ordering = ('-created',)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    json = models.TextField()
    is_valid = models.BooleanField(default=False)
    # Individual report fields - use `TextField` because there are no limits by any specification for these fields.
    document_uri = models.TextField(blank=True, null=True)
    referrer = models.TextField(blank=True, null=True)
    blocked_uri = models.TextField(blank=True, null=True)
    violated_directive = models.TextField(blank=True, null=True)
    original_policy = models.TextField(blank=True, null=True)
    effective_directive = models.TextField(blank=True, null=True)
    status_code = models.PositiveSmallIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    line_number = models.PositiveIntegerField(blank=True, null=True)
    column_number = models.PositiveIntegerField(blank=True, null=True)
    disposition = models.CharField(max_length=10, blank=True, null=True, choices=DISPOSITIONS)

    @property
    def data(self):
        """ Returns self.json loaded as a python object. """
        try:
            data = self._data
        except AttributeError:
            data = self._data = json.loads(self.json)
        return data

    def json_as_html(self):
        """ Print out self.json in a nice way. """

        # To avoid circular import
        from cspreports import utils

        formatted_json = utils.format_report(self.json)
        return mark_safe(u"<pre>\n%s</pre>" % escape(formatted_json))
