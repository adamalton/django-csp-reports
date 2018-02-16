# Django Content Security Policy Reports

[![Build Status](https://travis-ci.org/adamalton/django-csp-reports.svg)](https://travis-ci.org/adamalton/django-csp-reports)

A [Django](https://www.djangoproject.com) app for handling reports from web browsers of violations of your website's content security policy.

This app does not handle the setting of the [Content-Security-Policy](http://en.wikipedia.org/wiki/Content_Security_Policy) HTTP headers, but deals with handling the reports that web browsers may submit to your site (via the `report-uri`) when the stated content security policy is violated.

It is recommended that you use an app such as [django-csp](https://pypi.python.org/pypi/django_csp) ([Github](https://github.com/mozilla/django-csp)) to set the `Content-Security-Policy` headers.

### So What Does This Thing Do?

It receives the reports from the browser and does any/all of the following with them:

* Logs them using the python `logging` module.
* Sends them to you via email.
* Saves them to the datbase via a Django model.
* Runs any of your own custom functions on them.
* Can generate a summary of a reports.


### Supported Django Versions

Supports Python 2.7, 3.4 to 3.7 and Django 1.8 to 1.11.


### How Do I Use This Thing?

1. Install this app into your Django project somehow.
2. Add 'cspreports' to your `INSTALLED_APPS`.
3. Include `cspreports.urls` in your URL config somewhere.
4. In your `Content-Security-Policy` HTTP headers, set `reverse('report_csp')` as the `report-uri`.  (Note, with django-csp, you will want to set `CSP_REPORT_URI = reverse_lazy('report_csp')` in settings.py).
5. Set all/any of the following into settings.py as you so desire, hopefully they are self-explanatory:
    * `CSP_REPORTS_EMAIL_ADMINS` (`bool` defaults to `True`).
    * `CSP_REPORTS_LOG` (`bool` defaults to `True`).
    * `CSP_REPORTS_LOG_LEVEL` (`str`, one of the Python logging module's available log functions, defaults to `'warning'`).
    * `CSP_REPORTS_SAVE` (`bool` defaults to `True`).  Determines whether the reports are saved to the database.
    * `CSP_REPORTS_ADDITIONAL_HANDLERS` (`iterable` defaults to `[]`). Each value should be a dot-separated string path to a function which you want be called when a report is received. Each function is passed the `HttpRequest` of the CSP report.
    * `CSP_REPORTS_LOGGER_NAME` (`str` defaults to `CSP Reports`). Specifies the logger name that will be used for logging CSP reports, if enabled.
6. Set a cron to generate summaries.
7. Enjoy.


### Commands

#### `clean_cspreports`
Deletes old reports, but keeps reports over the last week (by default).

#### `make_csp_summary`
Generates a summary of CSP reports over the yesterday (by default).
