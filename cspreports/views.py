from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cspreports.utils import process_report


@require_POST
@csrf_exempt
def report_csp(request):
    """ The handler for browsers to send Content Security Policy violation reports to.
        The 'report-uri' in HTTP Content-Security-Policy headers should point to this view.
    """
    process_report(request)
    return HttpResponse('')
