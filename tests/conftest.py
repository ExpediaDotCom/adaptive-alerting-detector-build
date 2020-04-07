import copy
import json
import os
import pytest
import responses
import uuid

from adaptive_alerting_detector_build.metrics import Metric


GRAPHITE_MOCK_RESPONSE = json.loads(open("tests/data/graphite-mock.json").read())

GRAPHITE_SPARSE_DATA_MOCK_RESPONSE = json.loads(open("tests/data/graphite-mock-sparse-data.json").read())

DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE = json.loads(
    open("tests/data/detector-mappings-mock.json").read()
)

FIND_BY_MATCHING_TAGS_MOCK_RESPONSE = json.loads(
    open("tests/data/find-matching-by-tags-mock.json").read()
)

FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE = json.loads(
    open("tests/data/find-matching-by-tags-empty-mock.json").read()
)

MOCK_DETECTORS = json.loads(open("tests/data/detectors-mock.json").read())

METRIC_DETECTOR_MAPPINGS = json.loads(
    open("tests/data/metric-detector-mappings-mock.json").read()
)


@pytest.fixture
def mock_metric():
    def create_mock_metric(
        data=None, metric_type="LATENCY", model_service_url="http://modelservice"
    ):
        metric_config = {
            "type": metric_type,
            "tags": {"role": "my-web-app", "what": "elb_2xx"},
        }

        datasource_config = {"type": "mock"}
        if data:
            datasource_config["data"] = data
        return Metric(
            metric_config, datasource_config, model_service_url=model_service_url
        )

    return create_mock_metric
