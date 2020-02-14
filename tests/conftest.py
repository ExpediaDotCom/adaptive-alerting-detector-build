import copy
import json
import os
import pytest
import responses
import uuid

from adaptive_alerting_detector_build.metrics import Metric



# def pytest_generate_tests(metafunc):
#     os.environ["MODEL_SERVICE_USER"] = "test_username"



# @pytest.fixture(autouse=True)
# def set_env_defaults(monkeypatch):
#     """Set default settings for all tests"""

#     os.environ["MODEL_SERVICE_USER"] = "test_username"
# monkeypatch.setenv("MODEL_SERVICE_USER", "test_username")
# monkeypatch.delattr("requests.sessions.Session.request")
    



GRAPHITE_MOCK_RESPONSE = json.loads(open('tests/data/graphite-mock.json').read())

DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE = json.loads(
    open('tests/data/detector-mappings-mock.json').read())

FIND_BY_MATCHING_TAGS_MOCK_RESPONSE = json.loads(
    open('tests/data/find-matching-by-tags-mock.json').read())

FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE = json.loads(
    open('tests/data/find-matching-by-tags-empty-mock.json').read())

MOCK_DETECTORS =  json.loads(open('tests/data/detectors-mock.json').read())

METRIC_DETECTOR_MAPPINGS = json.loads(open("tests/data/metric-detector-mappings-mock.json").read())

@pytest.fixture
def mock_metric():
    metric_config = { 
        "type": "REQUEST_COUNT",
        "tags": {
            "role": "my-web-app", 
            "what": "elb_2xx"
    }}
    def create_mock_metric(data=None, config=metric_config, model_service_url="http://modelservice"):
        datasource_config = {
            "type": "mock"
        }
        if data:
            datasource_config["data"] = data
        return Metric(metric_config, datasource_config, model_service_url=model_service_url)

    return create_mock_metric