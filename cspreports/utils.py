# STANDARD LIB
import logging

# LIBRARIES
from django.conf import settings
from django.core.mail import mail_admins
from django.utils.importlib import import_module

# CSP REPORTS
from cspreports.models import CSPReport


logger = logging.getLogger("CSP Reports")


def process_report(report):
    """ Given the raw JSON string of a CSP violation report, log it in the required ways. """
    if config.EMAIL_ADMINS:
        email_admins(report)
    if config.LOG:
        log_report(report)
    if config.SAVE:
        save_report(report)
    if config.ADDITIONAL_HANDLERS:
        run_additional_handlers(report)


def email_admins(report):
    mail_admins("CSP Violation Report", report)


def log_report(report):
    func = getattr(logger, config.LOG_LEVEL)
    func("Content Security Policy violation: %s", report)


def save_report(report):
    CSPReport.objects.create(json=report)


def run_additional_handlers(report):
    for handler in get_additional_handlers():
        handler(report)


class Config(object):
    """ Configuration with defaults, each of which is overrideable in django settings. """
    PREFIX = "CSP_REPORTS_"

    # Defaults
    EMAIL_ADMINS = True
    LOG = True
    LOG_LEVEL = 'warning'
    SAVE = True
    ADDITIONAL_HANDLERS = []

    def __getattr__(self, name):
        try:
            return getattr(settings, "%s%s" % (self.PREFIX, name))
        except AttributeError:
            return getattr(self, name)


config = Config()
_additional_handlers = None


def get_additional_handlers():
    """ Returns the actual functions from the dotted paths specified in ADDITIONAL_HANDLERS. """
    if isinstance(_additional_handlers, list):
        return _additional_handlers
    handlers = ()
    for name in config.ADDITIONAL_HANDLERS:
        module_name, function_name = name.rsplit('.', 1)
        function = getattr(import_module(module_name), function_name)
        handlers += (function,)
