help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "flatdoc - opens the documentation in your browser"
	@echo "lint - check style with pylint"
	@echo "pytest - run tests and coverage with the default Python"
	@echo "test - runt tests and linter with the default Python"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr reports/


lint:
	mkdir -p reports
	pylint src tests --disable=E1111 --disable=C0111 --disable=C0103 --disable=C0103 --disable=C0330 --disable=R0913 --disable=R0902 --disable=R0903

pytest:
	py.test

mypy:
	mypy src tests

test: lint mypy pytest

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install
