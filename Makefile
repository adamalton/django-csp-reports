.PHONY: test coverage isort check-isort check-flake8

test:
	python runtests.py

coverage:
	python-coverage erase
	-rm -r htmlcov
	python-coverage run --branch --source="." runtests.py
	python-coverage html -d htmlcov

isort:
	isort cspreports

check-isort:
	isort --check-only --diff cspreports

check-flake8:
	flake8 --format=pylint cspreports
