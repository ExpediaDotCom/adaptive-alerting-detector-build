import logging
import responses
from adaptive_alerting_detector_build.cli import read_config_file, build_detectors_for_metric_configs
from tests.conftest import FIND_BY_MATCHING_TAGS_MOCK_RESPONSE
from tests.conftest import FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE
from tests.conftest import MOCK_DETECTORS
from tests.conftest import GRAPHITE_MOCK_RESPONSE

@responses.activate
def test_cli_build_detectors_alredy_exists(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_2xx'))|summarize('1min','sum')&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    metric_configs, exit_code = read_config_file("./tests/data/metric_config.json")
    build_exit_code = build_detectors_for_metric_configs(metric_configs)
    print(caplog.records)
    assert build_exit_code == 0
    assert len(caplog.records) == 4
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric_config.json"
    assert caplog.records[1].msg == "No detectors built for metric 'My App Request Count'"
    assert caplog.records[2].msg == "No detectors built for metric 'My App Error Count'"
    assert caplog.records[3].msg == "No detectors built for metric 'My App Success Rate'"


@responses.activate
def test_cli_build_new_detectors(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE,
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings",
            json=[],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/v2/detectors",
            body="4fdc3395-e969-449a-a306-201db183c6d7",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_2xx'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    responses.add(responses.POST, "http://modelservice/api/v2/detectors",
            body="49186d13-b106-476d-ba23-c332c325fb15",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=49186d13-b106-476d-ba23-c332c325fb15",
            json=MOCK_DETECTORS[1],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_5xx'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    responses.add(responses.POST, "http://modelservice/api/v2/detectors",
            body="16769303-a950-4d0f-a5a6-8d00eef886ec",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=16769303-a950-4d0f-a5a6-8d00eef886ec",
            json=MOCK_DETECTORS[2],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_success_rate'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    metric_configs, exit_code = read_config_file("./tests/data/metric_config.json")
    build_exit_code = build_detectors_for_metric_configs(metric_configs)
    assert build_exit_code == 0
    assert len(caplog.records) == 4
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric_config.json"
    assert caplog.records[1].msg == "New 'constant-detector' detector created with UUID: 4fdc3395-e969-449a-a306-201db183c6d7"
    assert caplog.records[2].msg == "New 'constant-detector' detector created with UUID: 49186d13-b106-476d-ba23-c332c325fb15"
    assert caplog.records[3].msg == "New 'constant-detector' detector created with UUID: 16769303-a950-4d0f-a5a6-8d00eef886ec"
