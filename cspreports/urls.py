from __future__ import unicode_literals

from django.conf.urls import url

from .views import report_csp

urlpatterns = [
    url(r'^report/$', report_csp, name='report_csp'),
]
