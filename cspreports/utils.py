import json
import logging
from datetime import datetime
from importlib import import_module

from django.conf import settings
from django.core.mail import mail_admins
from django.utils.dateparse import parse_date
from django.utils.timezone import localtime, make_aware, now

from cspreports.models import get_report_model
from cspreports.conf import app_settings

CSPReport = get_report_model()

logger = logging.getLogger(app_settings.LOGGER_NAME)


def process_report(request):
    """ Given the HTTP request of a CSP violation report, log it in the required ways. """
    if not should_process_report(request):
        return
    if app_settings.EMAIL_ADMINS:
        email_admins(request)
    if app_settings.LOG:
        log_report(request)
    if app_settings.SAVE:
        save_report(request)
    if app_settings.ADDITIONAL_HANDLERS:
        run_additional_handlers(request)


def format_report(jsn):
    """ Given a JSON report, return a nicely formatted (i.e. with indentation) string.
        This should handle invalid JSON (as the JSON comes from the browser/user).
        We trust that Python's json library is secure, but if the JSON is invalid then we still
        want to be able to display it, rather than tripping up on a ValueError.
    """
    if isinstance(jsn, bytes):
        jsn = jsn.decode('utf-8')
    try:
        return json.dumps(json.loads(jsn), indent=4, sort_keys=True, separators=(',', ': '))
    except ValueError:
        return "Invalid JSON. Raw dump is below.\n\n" + jsn


def email_admins(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    report = format_report(request.body)
    message = "User agent:\n%s\n\nReport:\n%s" % (user_agent, report)
    mail_admins("CSP Violation Report", message)


def log_report(request):
    func = getattr(logger, app_settings.LOG_LEVEL)
    func("Content Security Policy violation: %s", format_report(request.body))


def save_report(request):
    message = request.body
    if isinstance(message, bytes):
        message = message.decode(request.encoding or settings.DEFAULT_CHARSET)

    report = CSPReport.from_message(message)
    report.user_agent = request.META.get('HTTP_USER_AGENT', '')
    report.save()


def run_additional_handlers(request):
    for handler in get_additional_handlers():
        handler(request)


_additional_handlers = None
_filter_function = None


def get_additional_handlers():
    """ Returns the actual functions from the dotted paths specified in ADDITIONAL_HANDLERS. """
    global _additional_handlers
    if not isinstance(_additional_handlers, list):
        handlers = []
        for name in app_settings.ADDITIONAL_HANDLERS:
            function = import_from_dotted_path(name)
            handlers.append(function)
        _additional_handlers = handlers
    return _additional_handlers


def parse_date_input(value):
    """Return datetime based on the user's input.

    @param value: User's input
    @type value: str
    @raise ValueError: If the input is not valid.
    @return: Datetime of the beginning of the user's date.
    """
    try:
        limit = parse_date(value)
    except ValueError:
        limit = None
    if limit is None:
        raise ValueError("'{}' is not a valid date.".format(value))
    limit = datetime(limit.year, limit.month, limit.day)
    if settings.USE_TZ:
        limit = make_aware(limit)
    return limit


def get_midnight():
    """Return last midnight in localtime as datetime.

    @return: Midnight datetime
    """
    limit = now()
    if settings.USE_TZ:
        limit = localtime(limit)
    return limit.replace(hour=0, minute=0, second=0, microsecond=0)


def import_from_dotted_path(name):
    module_name, function_name = name.rsplit('.', 1)
    return getattr(import_module(module_name), function_name)


def should_process_report(request):
    if not app_settings.FILTER_FUNCTION:
        return True
    global _filter_function
    if _filter_function is None:
        _filter_function = import_from_dotted_path(app_settings.FILTER_FUNCTION)
    return _filter_function(request)
