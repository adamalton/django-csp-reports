from django.contrib import admin
from django.utils.html import format_html

from cspreports.models import CSPReport


class CSPReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'document_uri', 'blocked_uri')
    fields = ('created', 'modified', 'json_as_html')
    readonly_fields = ('created', 'modified', 'json_as_html')

    def json_as_html(self, instance):
        return format_html("<br />" + instance.json_as_html())

    def document_uri(self, instance):
        return instance.data.get('csp-report', {}).get('document-uri')

    def blocked_uri(self, instance):
        return instance.data.get('csp-report', {}).get('blocked-uri')

    json_as_html.short_description = "Report"


admin.site.register(CSPReport, CSPReportAdmin)
