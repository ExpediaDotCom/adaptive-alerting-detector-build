# adaptive-alerting-detector-build

Adaptive Alerting Detector Build Python Library

```
pip install git+https://github.com/ExpediaDotCom/adaptive-alerting-detector-build.git#egg=adaptive-alerting-detector-build
```

# Usage

## Configuration

```sh
# may also be passed when creating an instance of DetectorClient
MODEL_SERVICE_URL=http://modelservice
MODEL_SERVICE_USER=awesome_user

# optional, default=INFO
LOG_LEVEL=DEBUG
```

## Read Metrics JSON File and Build Detectors

```
# Load metric configuration Metric(config, datasource_config, optional: model_service_url)
metric = Metric({"tags": {"app": "myApplication", "metric": "request_count"}}, {"url": "http://graphite"})

# Get detectors assocated to the metric
metric.detectors

# Get detectors assocated to the metric
metric.detectors
```

# User Environment
## Setup
### Install `pipenv`

 ```$ brew install pipenv```

### Create virtual environment

```$ pipenv install```

## Install tools

```$ pipenv run setup.py```

## Use
### Use CLI tool

```$ adaptive-alerting -h```

# Development Environment
## Setup
### Install `pipenv`

 ```$ brew install pipenv```

### Setup environment and install dependencies

```$ make install```

## Run tests

```$ make test```

## Enter the pipenv shell

(See https://realpython.com/pipenv-guide/ for more info.)

```$ pipenv shell```

## Build

```$ make build```

