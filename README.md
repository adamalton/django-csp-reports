# Django Content Security Policy Reports

A [Django](https://www.djangoproject.com) app for handling reports from web browsers of violations of your website's content security policy.

This app does not handle the setting of the [Content-Security-Policy](http://en.wikipedia.org/wiki/Content_Security_Policy) HTTP headers, but deals with handling the reports that web browsers may submit to your site (via the `report-uri`) when the stated content security policy is violated.

It is recommended that you use an app such as [django-csp](https://pypi.python.org/pypi/django_csp) ([Github](https://github.com/mozilla/django-csp)) to set the `Content-Security-Policy` headers.

### So What Does This Thing Do?

It receives the reports from the browser and does any/all of the following with them:

* Logs them using the python `logging` module.
* Sends them to you via email.
* Saves them to the datbase via a Django model.
* Runs any of your own custom functions on them.


### How Do I Use This Thing?

1. Install this app into your Django project somehow.
2. Add 'cspreports' to your `INSTALLED_APPS`.
3. Include `cspreports.urls` in your URL config somewhere.
4. In your `Content-Security-Policy` HTTP headers, set `reverse('report_csp')` as the `report-uri`.  (Note, with django-csp, you will want to set `CSP_REPORT_URI = reverse_lazy('report_csp')` in settings.py).
5. Set all/any of the following into settings.py as you so desire, hopefully they are self-explanatory:
  * `EMAIL_ADMINS` (`bool`).
  * `LOG` (`bool`).
  * `LOG_LEVEL` (`str`, one of `'debug', 'info', 'warning', 'error', 'critical'`).
  * `SAVE` (`bool`).  Determines whether the reports are saved to the database.
  * `ADDITIONAL_HANDLERS` (`iterable` of callable objects, e.g. functions).  Note: this functionality isn't implemented yet.  Send me a pull request :-).
6. Enjoy.
7. Send me all your money.
8. Send me a pull request for any of the things on the TODO list.


### TODO

* Tests.
* Implement the `ADDITIONAL_HANDLERS` functionality so that they actually get called.
* In `utils.save_report`, decode the JSON and pull out individual field values, then save individual values into separate fields on the `CSPReport` model so that they can be searched/displayed in the Django admin.
