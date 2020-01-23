import copy
import json
import pytest
import responses

from adaptive_alerting_detector_build.metrics import Metric

GRAPHITE_MOCK_RESPONSE = json.loads(open("tests/data/graphite_mock.json").read())


# @pytest.fixture
# @responses.activate
# def test_metric():
#     responses.add(
#         responses.GET,
#         "http://graphite/render?target=sumSeries(seriesByTag('role=my-app-web','what=elb_2xx'))&from=-168hours&until=now&format=json",
#         json=GRAPHITE_MOCK_RESPONSE,
#         status=200,
#     )
#     metric_config = {"tags": {"role": "my-app-web", "what": "elb_2xx"}}
#     datasource_config = {"url": "http://graphite"}
#     return Metric(metric_config, datasource_config)


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


# @pytest.fixture
# def mock_metric():


#     return create_mock_metric

MOCK_METRIC_CONFIG = {"tags": {"role": "my-app-web", "what": "elb_2xx"}}


def mock_metric(data=None, metric_config=MOCK_METRIC_CONFIG):
    datasource_config = {"type": "mock"}
    if data:
        datasource_config["data"] = data
    return Metric(metric_config, datasource_config, "http://modelservice")
