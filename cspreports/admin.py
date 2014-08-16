from django.contrib import admin

# SOCKET SHARE
from cspreports.models import CSPReport

class CSPReportAdmin(admin.ModelAdmin):
    list_display = ('created',)
    fields = ('created', 'modified', 'json_as_html')
    readonly_fields = ('created', 'modified', 'json_as_html')

    def json_as_html(self, instance):
        return "<br />" + instance.json_as_html()

    json_as_html.short_description = "Report"
    json_as_html.allow_tags = True

admin.site.register(CSPReport, CSPReportAdmin)
