#LIBRARIES
from django.db import models
from django.utils.html import escape
from django.utils.safestring import mark_safe


class CSPReport(models.Model):

    class Meta(object):
        ordering = ('-created',)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    json = models.TextField()

    def json_as_html(self):
        """ Print out self.json in a nice way. """

        # To avoid circular import
        from cspreports import utils

        formatted_json = utils.format_report(self.json)
        return mark_safe(u"<pre>\n%s</pre>" % escape(formatted_json))

