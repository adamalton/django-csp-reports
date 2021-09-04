""" Filters for use with the  setting. """
import json


def filter_browser_extensions(request):
    """ Filters out reports of CSP violations which are caused by browser extensions from common
        web browsers trying to inject resources.
    """
    json_str = request.body
    if isinstance(json_str, bytes):
        json_str = json_str.decode(request.encoding or "utf-8")
    try:
        report = json.loads(json_str).get("csp-report", {})
    except json.decoder.JSONDecodeError:
        return False
    # Ignore reports caused by browser extensions trying to load stuff
    src_file = report.get("source-file", "")
    ignored_prefixes = (
        "safari-extension://",
        "safari-web-extension://",
        "moz-extension://",
        "chrome-extension://",
    )
    if any(src_file.startswith(prefix) for prefix in ignored_prefixes):
        return False
    return True
