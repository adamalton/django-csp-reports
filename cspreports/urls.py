from django.conf.urls import re_path

from .views import report_csp

urlpatterns = [
    re_path(r'^report/$', report_csp, name='report_csp'),
]
