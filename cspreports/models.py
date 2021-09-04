# STANDARD LIB
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe

DISPOSITIONS = (
    ('enforce', 'enforce'),
    ('report', 'report'),
)

# Map of required CSP report fields to model fields
REQUIRED_FIELDS = (
    ('document-uri', 'document_uri'),
    ('referrer', 'referrer'),
    ('blocked-uri', 'blocked_uri'),
    ('violated-directive', 'violated_directive'),
    ('original-policy', 'original_policy'),
)
# Map of optional (CSP >= 2.0) CSP report fields to model fields
OPTIONAL_FIELDS = (
    ('disposition', 'disposition'),
    ('effective-directive', 'effective_directive'),
    ('source-file', 'source_file'),
    ('status-code', 'status_code'),
    ('line-number', 'line_number'),
    ('column-number', 'column_number'),
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

    class Meta:
        ordering = ('-created',)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_agent = models.TextField(blank=True)
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
    def nice_report(self):
        """Return a nicely formatted original report."""
        if not self.json:
            return '[no CSP report data]'
        try:
            data = json.loads(self.json)
        except ValueError:
            return "Invalid CSP report: '{}'".format(self.json)
        if 'csp-report' not in data:
            return 'Invalid CSP report: ' + json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))
        return json.dumps(data['csp-report'], indent=4, sort_keys=True, separators=(',', ': '))

    def __str__(self):
        return self.nice_report

    @classmethod
    def from_message(cls, message):
        """Creates an instance from CSP report message.

        If the message is not valid, the result will still have as much fields set as possible.

        @param message: JSON encoded CSP report.
        @type message: text
        """
        self = cls(json=message)
        try:
            decoded_data = json.loads(message)
        except ValueError:
            # Message is not a valid JSON. Return as invalid.
            return self
        try:
            report_data = decoded_data['csp-report']
        except KeyError:
            # Message is not a valid CSP report. Return as invalid.
            return self

        is_valid = True

        fields = REQUIRED_FIELDS + OPTIONAL_FIELDS
        for json_field_name, django_field_name in fields:
            value = report_data.get(json_field_name)
            # Try to pass the value through as much of Django's coercion/cleaning as possible, but
            # if the data is not entirely valid that's not a reason to not still save the report
            # if we can; even if the data isn't perfect, some information is better than none.
            to_python = cls._meta.get_field(django_field_name).to_python
            clean = cls._meta.get_field(django_field_name).clean
            try:
                value = to_python(value)
                # If the first conversion step worked, then store the value, even if the next
                # conversion fails
                setattr(self, django_field_name, value)
                value = clean(value, model_instance=self)
                setattr(self, django_field_name, value)
            except ValidationError:
                is_valid = False

        # Go through the REQUIRED_FIELDS list and make sure that a valid value was supplied for
        # each of them. Note that for str-type fields we treat a value of "" as valid, but if the
        # field is missing entirely (i.e. is None) we treat that as invalid. I (Adam) am not sure
        # if that's the correct way to do it, but it appears to be how we're doing it. Also note
        # that our model fields have null=True for these required fields, and if we took that off
        # then this block of code might be unnecessary, as the block of code above would catch the
        # ValidationError and set `is_valid` to False for us.
        for field, django_field_name in REQUIRED_FIELDS:
            field_value = getattr(self, django_field_name)
            if field_value is None:
                is_valid = False
                break
        self.is_valid = is_valid

        return self

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
        return mark_safe("<pre>\n%s</pre>" % escape(formatted_json))
