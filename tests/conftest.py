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
    



GRAPHITE_MOCK_RESPONSE = json.loads(open('tests/data/graphite_mock.json').read())

FIND_BY_MATCHING_TAGS_MOCK_RESPONSE = json.loads(
    open('tests/data/find_matching_by_tags_mock.json').read())

FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE = json.loads(
    open('tests/data/find_matching_by_tags_empty_mock.json').read())

MOCK_DETECTORS =  json.loads(open('tests/data/detectors_mock.json').read())

METRIC_DETECTOR_MAPPINGS = json.loads(open("tests/data/metric_detector_mappings_mock.json").read())

@pytest.fixture
@responses.activate
def test_metric():
    responses.add(responses.GET, "http://graphite/render?target=sumSeries(seriesByTag('role=my-app-web','what=elb_2xx'))&from=-168hours&until=now&format=json",
                json=GRAPHITE_MOCK_RESPONSE,
                status=200)
    metric_config = { 
        "tags": {
            "role": "my-app-web", 
            "what": "elb_2xx"
    }}
    datasource_config = {
        "url": "http://graphite"
    }
    return Metric(metric_config, datasource_config, model_service_url="http://modelservice")


# @pytest.fixture
# def mock_metric_data():
#     with responses.RequestsMock() as rsps:
#         graphite_mock_response_one_datapoint = copy.deepcopy(GRAPHITE_MOCK_RESPONSE)
#         graphite_mock_response_one_datapoint[0]["datapoints"] = [[5659.0, 1578524340]]
#         rsps.add(responses.GET, "http://graphite/render?target=sumSeries(seriesByTag('role=my-app-web','what=elb_2xx'))&from=-168hours&until=now&format=json",
#                     json=graphite_mock_response_one_datapoint,
#                     status=200)
#         yield rsps

# def test_api(mocked_responses):
#     mocked_responses.add(
#         responses.GET, 'http://twitter.com/api/1/foobar',
#         body='{}', status=200,
#         content_type='application/json')
#     resp = requests.get('http://twitter.com/api/1/foobar')
#     assert resp.status_code == 200

@pytest.fixture
def mock_metric():
    metric_config = { 
        "tags": {
            "role": "my-app-web", 
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