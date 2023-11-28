from django.contrib import admin
from django.utils.safestring import mark_safe

from cspreports.models import CSPReport


class CSPReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'document_uri', 'blocked_uri', 'is_valid')
    fields = ('created', 'modified', 'json_as_html')
    readonly_fields = ('created', 'modified', 'json_as_html')
    search_fields = ('json',)
    list_filter = ('is_valid',)
    date_hierarchy = 'created'

    def json_as_html(self, instance):
        return mark_safe("<br />" + instance.json_as_html())

    def document_uri(self, instance):
        return instance.data.get('csp-report', {}).get('document-uri')

    def blocked_uri(self, instance):
        return instance.data.get('csp-report', {}).get('blocked-uri')

    json_as_html.short_description = "Report"
    json_as_html.allow_tags = True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(CSPReport, CSPReportAdmin)
