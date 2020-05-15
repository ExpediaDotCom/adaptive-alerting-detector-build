.DEFAULT_GOAL := build 

clean :
	pipenv --rm

install :
	pipenv install --dev --skip-lock 

test :
	pipenv run pytest --verbose --cov-report term --cov-report html:build/coverage --cov=adaptive_alerting_detector_build tests

style :
	pipenv run black adaptive_alerting_detector_build --check


publish :
	pipenv run pip install 'twine>=1.5.0'
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/*
	rm -rf build dist .egg requests.egg-info

.PHONY: build
build :
	pipenv lock --requirements > requirements.txt
	pipenv install --dev
	pipenv run pipenv-setup sync
	# see https://github.com/pypa/pipenv/issues/3860
	export PIPENV_PYUP_API_KEY="" && pipenv check