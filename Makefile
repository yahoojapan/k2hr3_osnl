#
# K2HR3 OpenStack Notification Listener
#
# Copyright 2018 Yahoo! Japan Corporation.
#
# K2HR3 is K2hdkc based Resource and Roles and policy Rules, gathers 
# common management information for the cloud.
# K2HR3 can dynamically manage information as "who", "what", "operate".
# These are stored as roles, resources, policies in K2hdkc, and the
# client system can dynamically read and modify these information.
#
# For the full copyright and license information, please view
# the licenses file that was distributed with this source code.
#
# AUTHOR:   Hirotaka Wakabayashi
# CREATE:   Tue Sep 11 2018 
# REVISION:
#

.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python3 -c "$$BROWSER_PYSCRIPT"

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

init:
	python3 -m pip install pipenv
	pipenv install --skip-lock
	pipenv graph
	pipenv install --dev

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	rm -f VERSION RPMSPEC_VERSION

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr ..mypy_cache/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 --version
	flake8 k2hr3_osnl tests
	mypy k2hr3_osnl tests
	pylint k2hr3_osnl tests --py3k -r n
	python3 -m pip install collective.checkdocs
	python3 setup.py checkdocs

test: ## run tests quickly with the default Python
	python3 -m unittest

version:
	@rm -f VERSION RPMSPEC_VERSION
	@perl -ne 'print if /^[0-9]+.[0-9]+.[0-9]+ \([0-9]{4}-[0-9]{2}-[0-9]{2}\)$$/' HISTORY.rst \
		| head -n 1 | perl -lne 'print $$1 if /^([0-9]+.[0-9]+.[0-9]+) \(.*\)/' > VERSION
	@perl -ne 'print $$2 if /^Version:(\s+)([0-9]+.[0-9]+.[0-9]+)$$/' python-k2hr3-osnl.spec > RPMSPEC_VERSION

SOURCE_VERSION = $(shell python3 -c 'import k2hr3_osnl; print(k2hr3_osnl.version())')
HISTORY_VERSION = $(shell cat VERSION)
RPMSPEC_VERSION = $(shell cat RPMSPEC_VERSION)

test-with-version: version ## builds source and wheel package
	@echo 'source  ' ${SOURCE_VERSION}
	@echo 'history ' ${HISTORY_VERSION}
	@echo 'rpmspec ' ${RPMSPEC_VERSION}
	@if test "${SOURCE_VERSION}" = "${HISTORY_VERSION}" -a "${HISTORY_VERSION}" = "${RPMSPEC_VERSION}" ; then \
		python3 -m unittest ; \
	fi

test-all: lint test-version

coverage: ## check code coverage quickly with the default Python
	coverage run --source k2hr3_osnl -m unittest
	coverage report -m
	coverage xml
	coverage html
#	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/k2hr3_osnl.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ k2hr3_osnl
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
#	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine check dist/*
	twine upload dist/*

test-release:
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

dist: clean version ## builds source and wheel package
	@echo 'source  ' ${SOURCE_VERSION}
	@echo 'history ' ${HISTORY_VERSION}
	@if test "${SOURCE_VERSION}" = "${HISTORY_VERSION}" -a "${HISTORY_VERSION}" = "${RPMSPEC_VERSION}" ; then \
		python3 setup.py sdist ; \
		python3 setup.py bdist_wheel ; \
		ls -l dist ; \
	fi

install: clean ## install the package to the active Python's site-packages
	python3 setup.py install

#
# VIM modelines
#
# vim:set ts=4 fenc=utf-8:
#
