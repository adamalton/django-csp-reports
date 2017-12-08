.PHONY: isort check-isort check-flake8

isort:
	isort --recursive cspreports

check-isort:
	isort --check-only --diff --recursive cspreports

check-flake8:
	flake8 --format=pylint cspreports
