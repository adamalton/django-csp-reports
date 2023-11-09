from django.conf import settings


class Settings:
    """
    Shadow Django's settings with a little logic
    """

    @property
    def EMAIL_ADMINS(self):
        return getattr(settings, "CSP_REPORTS_EMAIL_ADMINS", True)

    @property
    def LOG(self):
        return getattr(settings, "CSP_REPORTS_LOG", True)

    @property
    def LOG_LEVEL(self):
        return getattr(settings, "CSP_REPORTS_LOG_LEVEL", "warning")

    @property
    def LOGGER_NAME(self):
        return getattr(settings, "CSP_REPORTS_LOGGER_NAME", "CSP Reports")

    @property
    def SAVE(self):
        return getattr(settings, "CSP_REPORTS_SAVE", True)

    @property
    def ADDITIONAL_HANDLERS(self):
        return getattr(settings, "CSP_REPORTS_ADDITIONAL_HANDLERS", [])

    @property
    def FILTER_FUNCTION(self):
        return getattr(settings, "CSP_REPORTS_FILTER_FUNCTION", None)


app_settings = Settings()
