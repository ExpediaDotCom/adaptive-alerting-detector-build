.DEFAULT_GOAL := build

.PHONY: clean
clean:
	pipenv --rm

.PHONY: build
build:
	pipenv install --dev
	pipenv run pipenv-setup sync
	test
	style
	pipenv check

.PHONY: install
install:
	pipenv install --dev --skip-lock 

.PHONY: test
test:
	pipenv run pytest --verbose --cov-report term --cov-report html:build/coverage --cov=adaptivealerting tests

.PHONY: style
style:
	pipenv run black adaptivealerting --check

.PHONY: publish
publish:
	pipenv run pip install 'twine>=1.5.0'
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/*
	rm -rf build dist .egg requests.egg-info

