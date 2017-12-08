from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin

from .views import report_csp

admin.autodiscover()


urlpatterns = [
    url(r'^report/$', report_csp, name='report_csp'),
]
