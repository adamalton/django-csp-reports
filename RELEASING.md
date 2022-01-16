Releasing
============

This file is here for the benefit of the package author, who can never remember what all the steps are to release this to PyPi and GitHub.

1. Bump the `VERSION` in `setup.py`.
2. Run `python setup.py sdist bdist_wheel`.
3. Run `pip install twine` if it's not already installed.
4. Run `twine check dist/django-csp-reports-VERSION*`
5. Run `twine upload --repository-url https://test.pypi.org/legacy/ dist/django-csp-reports-VERSION*`
6. Check that that worked.
7. Run `twine upload dist/django-csp-reports-VERSION*`
8. Check that that worked.
9. Push the VERSION bump to GitHub.
10. Tag the release: `git tag VERSION && git push origin VERSION`
10. Release it on GitHub, uploading the `.tar.gz` file from the `dist/` directory: https://github.com/adamalton/django-csp-reports/releases/new
 

See: https://realpython.com/pypi-publish-python-package/.
