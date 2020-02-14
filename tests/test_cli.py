import logging
from freezegun import freeze_time
import responses
from adaptive_alerting_detector_build.cli import read_config_file, build_detectors_for_metric_configs
from adaptive_alerting_detector_build.cli import delete_detectors_for_metric_configs
from adaptive_alerting_detector_build.cli import train_detectors_for_metric_configs
from tests.conftest import FIND_BY_MATCHING_TAGS_MOCK_RESPONSE
from tests.conftest import FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE
from tests.conftest import MOCK_DETECTORS
from tests.conftest import GRAPHITE_MOCK_RESPONSE
from tests.conftest import DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE

@responses.activate
def test_cli_build_detectors_already_exists(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    metric_configs, exit_code = read_config_file("./tests/data/metric-config.json")
    build_exit_code = build_detectors_for_metric_configs(metric_configs)
    print(caplog.records)
    assert build_exit_code == 0
    assert len(caplog.records) == 4
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config.json"
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
            body="47a0661d-aceb-4ef2-bf06-0828f28631b4",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
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
    metric_configs, exit_code = read_config_file("./tests/data/metric-config.json")
    build_exit_code = build_detectors_for_metric_configs(metric_configs)
    assert build_exit_code == 0
    assert len(caplog.records) == 4
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config.json"
    assert caplog.records[1].msg == "New 'constant-detector' detector created with UUID: 4fdc3395-e969-449a-a306-201db183c6d7"
    assert caplog.records[2].msg == "New 'constant-detector' detector created with UUID: 47a0661d-aceb-4ef2-bf06-0828f28631b4"
    assert caplog.records[3].msg == "New 'constant-detector' detector created with UUID: 16769303-a950-4d0f-a5a6-8d00eef886ec"

@responses.activate
def test_cli_delete_metric_detectors(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[0]],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[1]],
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/detectorMappings?id=5XeANXABlK1-eG-Fo78V",
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/detectorMappings?id=6XeANXABlK1-eG-Fo78V",
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/v2/detectors?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/v2/detectors?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            status=200)
    metric_configs, exit_code = read_config_file("./tests/data/metric-config-request-count.json")
    delete_exit_code = delete_detectors_for_metric_configs(metric_configs)
    assert delete_exit_code == 0
    assert len(caplog.records) == 3
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config-request-count.json"
    assert caplog.records[1].msg == "Detector/Detector Mapping with UUID '4fdc3395-e969-449a-a306-201db183c6d7' deleted."
    assert caplog.records[2].msg == "Detector/Detector Mapping with UUID '47a0661d-aceb-4ef2-bf06-0828f28631b4' deleted."

@responses.activate
def test_cli_train_metric_detectors(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[0]],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[1]],
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/detectorMappings?id=5XeANXABlK1-eG-Fo78V",
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/detectorMappings?id=6XeANXABlK1-eG-Fo78V",
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/v2/detectors?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            status=200)
    responses.add(responses.DELETE, "http://modelservice/api/v2/detectors?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            status=200)
    metric_configs, exit_code = read_config_file("./tests/data/metric-config-request-count.json")
    delete_exit_code = delete_detectors_for_metric_configs(metric_configs)
    assert delete_exit_code == 0
    assert len(caplog.records) == 3
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config-request-count.json"
    assert caplog.records[1].msg == "Detector/Detector Mapping with UUID '4fdc3395-e969-449a-a306-201db183c6d7' deleted."
    assert caplog.records[2].msg == "Detector/Detector Mapping with UUID '47a0661d-aceb-4ef2-bf06-0828f28631b4' deleted."


@responses.activate
@freeze_time("2019-11-15")
def test_cli_train_metric_detectors(caplog):
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
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_2xx'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    responses.add(responses.PUT, "http://modelservice/api/v2/detectors?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            status=200)
    metric_configs, exit_code = read_config_file("./tests/data/metric-config-request-count.json")
    train_exit_code = train_detectors_for_metric_configs(metric_configs)
    assert train_exit_code == 0
    assert len(caplog.records) == 3
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config-request-count.json"
    assert caplog.records[1].msg == "Trained 'constant-detector' detector with UUID: 4fdc3395-e969-449a-a306-201db183c6d7"
    assert caplog.records[2].msg == "Training not required for 'constant-detector' detector with UUID: 47a0661d-aceb-4ef2-bf06-0828f28631b4"
