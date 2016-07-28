from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cspreports.views',
    url(r'^report/$', 'report_csp', name='report_csp'),
)
