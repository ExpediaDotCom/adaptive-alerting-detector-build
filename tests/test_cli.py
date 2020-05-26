from adaptive_alerting_detector_build.cli import disable_detectors_for_metric_configs
from adaptive_alerting_detector_build.cli import read_config_file, build_detectors_for_metric_configs
from adaptive_alerting_detector_build.cli import train_detectors_for_metric_configs
from adaptive_alerting_detector_build.cli import diff_metric_configs

from freezegun import freeze_time
import logging
import responses

from tests.conftest import DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE
from tests.conftest import FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE
from tests.conftest import FIND_BY_MATCHING_TAGS_MOCK_RESPONSE
from tests.conftest import GRAPHITE_MOCK_RESPONSE
from tests.conftest import GRAPHITE_SPARSE_DATA_MOCK_RESPONSE
from tests.conftest import MOCK_DETECTORS



@responses.activate
def test_cli_build_detectors_already_exists(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    metric_configs, exit_code = read_config_file("./tests/data/metric-config.json")
    build_exit_code = build_detectors_for_metric_configs(metric_configs)
    print(caplog.records)
    assert build_exit_code == 0
    assert len(caplog.records) == 5
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config.json"
    assert caplog.records[1].msg == "No detectors built for metric 'My App Request Count'"
    assert caplog.records[2].msg == "No detectors built for metric 'My App Error Count'"
    assert caplog.records[3].msg == "No detectors built for metric 'My App Success Rate'"
    assert caplog.records[4].msg == "No detectors built for metric 'My App Latency'"


@responses.activate
def test_cli_build_new_detectors(caplog):

    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE,
            status=200)

    # request_count
    responses.add(responses.POST, "http://modelservice/api/detectorMappings",
            json=[],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/v3/detectors",
            body="4fdc3395-e969-449a-a306-201db183c6d7",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_2xx'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    # error_count
    responses.add(responses.POST, "http://modelservice/api/v3/detectors",
            body="47a0661d-aceb-4ef2-bf06-0828f28631b4",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_5xx'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    # success_rate
    responses.add(responses.POST, "http://modelservice/api/v3/detectors",
            body="16769303-a950-4d0f-a5a6-8d00eef886ec",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=16769303-a950-4d0f-a5a6-8d00eef886ec",
            json=MOCK_DETECTORS[2],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=elb_success_rate'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    # latency
    responses.add(responses.POST, "http://modelservice/api/v3/detectors",
            body="5afc2bb3-4a5b-4a4b-8e30-890d67904588",
            status=201)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=5afc2bb3-4a5b-4a4b-8e30-890d67904588",
            json=MOCK_DETECTORS[3],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=tp90'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    metric_configs, exit_code = read_config_file("./tests/data/metric-config.json")
    build_exit_code = build_detectors_for_metric_configs(metric_configs)
    assert build_exit_code == 0
    assert len(caplog.records) == 5
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config.json"
    assert caplog.records[1].msg == "New 'constant-detector' detector created with UUID: 4fdc3395-e969-449a-a306-201db183c6d7"
    assert caplog.records[2].msg == "New 'constant-detector' detector created with UUID: 47a0661d-aceb-4ef2-bf06-0828f28631b4"
    assert caplog.records[3].msg == "New 'constant-detector' detector created with UUID: 16769303-a950-4d0f-a5a6-8d00eef886ec"
    assert caplog.records[4].msg == "New 'constant-detector' detector created with UUID: 5afc2bb3-4a5b-4a4b-8e30-890d67904588"


@responses.activate
def test_cli_disable_metric_detectors(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[0]],
            status=200)
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[1]],
            status=200)
    responses.add(responses.PUT, "http://modelservice/api/detectorMappings/disable?id=5XeANXABlK1-eG-Fo78V",
            status=200)
    responses.add(responses.PUT, "http://modelservice/api/detectorMappings/disable?id=6XeANXABlK1-eG-Fo78V",
            status=200)
    responses.add(responses.POST, "http://modelservice/api/v3/detectors/toggleDetector?enabled=false&uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            status=200)
    responses.add(responses.POST, "http://modelservice/api/v3/detectors/toggleDetector?enabled=false&uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            status=200)
    metric_configs, exit_code = read_config_file("./tests/data/metric-config-request-count.json")
    disable_exit_code = disable_detectors_for_metric_configs(metric_configs)
    assert disable_exit_code == 0
    assert len(caplog.records) == 3
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config-request-count.json"
    assert caplog.records[1].msg == "Detector/Detector Mapping with UUID '4fdc3395-e969-449a-a306-201db183c6d7' disabled."
    assert caplog.records[2].msg == "Detector/Detector Mapping with UUID '47a0661d-aceb-4ef2-bf06-0828f28631b4' disabled."

@responses.activate
def test_cli_train_metric_detectors_sparse_data(caplog):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
        json={ "groupedDetectorsBySearchIndex": 
                { "0": [
                        { "uuid": "5afc2bb3-4a5b-4a4b-8e30-890d67904588" }
                ]},
                "lookupTimeInMillis": 2
                },
        status=200)
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=5afc2bb3-4a5b-4a4b-8e30-890d67904588",
            json=MOCK_DETECTORS[3],
            status=200)
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('app=my-web-app','what=tp90'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_SPARSE_DATA_MOCK_RESPONSE,
        status=200,
    )

    metric_configs, exit_code = read_config_file("./tests/data/metric-config-latency.json")
    train_exit_code = train_detectors_for_metric_configs(metric_configs)
    assert train_exit_code == 0
    assert len(caplog.records) == 2
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config-latency.json"
    assert caplog.records[1].msg == "Unable to train detector for metric 'My App Request Latency',  Sample must have at least thirty elements! Skipping!"

@responses.activate
def test_cli_invalid_metric_config(caplog):
    metric_configs, exit_code = read_config_file("./tests/data/invalid-metric-config.json")
    assert exit_code == 0
    assert len(caplog.records) == 2
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/invalid-metric-config.json"
    assert caplog.records[1].msg == "Exception ValueError while reading config file 'Failed to convert value (INVALID_METRIC_TYPE) to child object class (<enum 'MetricType'>). ... [Original error message: 'INVALID_METRIC_TYPE' is not a valid MetricType]'! Skipping!"

@responses.activate
def test_cli_missing_metric_config_file(caplog):
    metric_configs, exit_code = read_config_file("./tests/data/missing-metric-config.json")
    assert exit_code == 1
    assert len(caplog.records) == 2
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/missing-metric-config.json"
    assert caplog.records[1].msg == "Exception FileNotFoundError while reading config file './tests/data/missing-metric-config.json'! Skipping!"


@responses.activate
def test_cli_diff_metric_configs(caplog):
    previous, exit_code = read_config_file("./tests/data/metric-config.json")
    assert exit_code == 0
    current, exit_code = read_config_file("./tests/data/metric-config-v2.json")
    assert len(caplog.records) == 2
    assert caplog.records[0].msg == "Reading configuration file: ./tests/data/metric-config.json"
    assert caplog.records[1].msg == "Reading configuration file: ./tests/data/metric-config-v2.json"
    diff = diff_metric_configs(previous, current)
    assert len(diff["added"]) == 1
    assert diff["added"][0]["name"] == "My App Request Count Fixed"
    assert len(diff["modified"]) == 1
    assert diff["modified"][0]["name"] == "My App Error Count"
    assert len(diff["deleted"]) == 1
    assert diff["deleted"][0]["name"] == "My App Request Count"


