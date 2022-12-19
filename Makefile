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

# Initialize development environment
# Initialization fails if dependency problems happens or security vulnerabilities are detected.
#
# Note: 
# Make sure python3-devel or python3-dev is installed. Because oslo-message(or dependent libs) requires Python.h
init:
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade pipenv
	pipenv install --dev --skip-lock
	pipenv graph
	pipenv check

# Lint code and docs
# lint fails if there are syntax errors or undefined names.
#
# Note:
# lint commands should be emit in virtualenv activated environment.
lint:
	pipenv run flake8 --version
	pipenv run flake8 k2hr3_osnl tests
	pipenv run mypy k2hr3_osnl tests
	pipenv run pylint k2hr3_osnl tests -r n
	pipenv run python3 setup.py checkdocs

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

test-only: ## run tests quickly with the default Python
	pipenv run python3 -m unittest

# Check version strings consistency
# Make sure the following version strings are same. 
# 1. HISTORY.rst
# 2. python-k2hr3-osnl.spec
# 3. __init__.py
version:
	@rm -f VERSION RPMSPEC_VERSION
	@perl -ne 'print if /^[0-9]+.[0-9]+.[0-9]+ \([0-9]{4}-[0-9]{2}-[0-9]{2}\)$$/' HISTORY.rst \
		| head -n 1 | perl -lne 'print $$1 if /^([0-9]+.[0-9]+.[0-9]+) \(.*\)/' > VERSION
	@perl -ne 'print $$2 if /^Version:(\s+)([0-9]+.[0-9]+.[0-9]+)$$/' python-k2hr3-osnl.spec > RPMSPEC_VERSION

SOURCE_VERSION = $(shell pipenv run python3 -c 'import k2hr3_osnl; print(k2hr3_osnl.version())')
HISTORY_VERSION = $(shell cat VERSION)
RPMSPEC_VERSION = $(shell cat RPMSPEC_VERSION)

# Check version strings consistency
# Make sure the following version strings are same. 
# 1. HISTORY.rst
# 2. python-k2hr3-osnl.spec
# 3. __init__.py
test: version ## builds source and wheel package
	@echo 'source  ' ${SOURCE_VERSION}
	@echo 'history ' ${HISTORY_VERSION}
	@echo 'rpmspec ' ${RPMSPEC_VERSION}
	@if test "${SOURCE_VERSION}" = "${HISTORY_VERSION}" -a "${HISTORY_VERSION}" = "${RPMSPEC_VERSION}" ; then \
		pipenv run python3 -m unittest ; \
	else \
		exit 1; \
	fi

test-all: lint test

coverage: ## check code coverage quickly with the default Python
	pipenv run coverage run --source k2hr3_osnl -m unittest
	pipenv run coverage report -m
	pipenv run coverage xml
	pipenv run coverage html
#	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/k2hr3_osnl.rst
	rm -f docs/modules.rst
	pipenv run sphinx-apidoc -o docs/ k2hr3_osnl
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
#	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	pipenv run watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	pipenv run twine check dist/*
	pipenv run twine upload dist/*

test-release:
	pipenv run twine check dist/*
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

dist: clean version ## builds source and wheel package
	@echo 'source  ' ${SOURCE_VERSION}
	@echo 'history ' ${HISTORY_VERSION}
	@if test "${SOURCE_VERSION}" = "${HISTORY_VERSION}" -a "${HISTORY_VERSION}" = "${RPMSPEC_VERSION}" ; then \
		pipenv run python3 setup.py sdist ; \
		pipenv run python3 setup.py bdist_wheel ; \
		ls -l dist ; \
	fi

install: clean ## install the package to the active Python's site-packages
	pipenv run python3 setup.py install

#
# VIM modelines
#
# vim:set ts=4 fenc=utf-8:
#
