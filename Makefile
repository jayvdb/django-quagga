.PHONY: clean-pyc clean-build docs

help:
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc  ## Remove build artifacts and all pyc files

clean-build:  ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:  ## Remove generated Python files
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:  ## Run flake8
	flake8 zebra tests

test:  ## Run tests
	python setup.py test

test-all:  ## Run tests across all specified environments
	tox

coverage:  ## Run tests and build coverage report
	coverage run --source zebra setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:  ## Build the docs
	rm -f docs/zebra.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ zebra
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

build: clean  ## Create distribution files for release
	python setup.py sdist bdist_wheel

release: build  ## Create distribution files and publish to PyPI
	python setup.py check -r -s
	twine upload dist/*

sdist: clean  ## Create source distribution only
	python setup.py sdist
	ls -l dist
