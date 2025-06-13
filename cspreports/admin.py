from django.contrib import admin

from cspreports.models import get_report_model

CSPReport = get_report_model()


class CSPReportAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "document_uri", "blocked_uri", "is_valid")
    fields = ("created", "modified", "json_as_html")
    readonly_fields = ("created", "modified", "json_as_html")
    search_fields = ("json",)
    list_filter = ("is_valid",)
    date_hierarchy = "created"

    def json_as_html(self, instance):
        return "<br />" + instance.json_as_html()

    def document_uri(self, instance):
        return instance.data.get("csp-report", {}).get("document-uri")

    def blocked_uri(self, instance):
        return instance.data.get("csp-report", {}).get("blocked-uri")

    json_as_html.short_description = "Report"
    json_as_html.allow_tags = True


admin.site.register(CSPReport, CSPReportAdmin)
