from adaptive_alerting_detector_build.metrics import Metric
from adaptive_alerting_detector_build.config import MODEL_SERVICE_URL
from adaptive_alerting_detector_build.detectors import Detector, DetectorClient
import pandas as pd
import pytest
from freezegun import freeze_time
import responses
import json
from math import isclose
from tests.conftest import FIND_BY_MATCHING_TAGS_MOCK_RESPONSE
from tests.conftest import FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE
from tests.conftest import MOCK_DETECTORS
from tests.conftest import DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE


@responses.activate
def test_detector_client_list_detectors_for_metric(mock_metric):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    detector_client = DetectorClient()
    test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    detectors = detector_client.list_detectors_for_metric(test_metric.config["tags"])
    for detector in detectors:
        assert isinstance(detector, Detector)
    assert len(detectors) == 2
    assert len(test_metric.detectors) == 2

@responses.activate
def test_build_metric_detectors(mock_metric):
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

    test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    assert len(test_metric.detectors) == 0
    new_detectors = test_metric.build_detectors()
    assert len(new_detectors) == 1
    # TODO: graphite returns valid data
    # TODO: responses.add model service get detectors for metric (return none)
    # TODO: responses.add model service create detector / mapping
    # detector_config={}
    # test_metric_detector = test_metric_detector(test_metric, detector_config)
    # test_metric_detector.train()
    # test_metric_detector.save()
    # assert test_metric_detector.state=="TRUSTED"


@responses.activate
def test_delete_metric_detectors(mock_metric):
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
    test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    assert len(test_metric.detectors) == 2
    test_metric.delete_detectors()
    responses.reset()
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
        json=FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE,
        status=200)
    assert len(test_metric.detectors) == 0


@responses.activate
@freeze_time("2019-11-15")
def test_train_metric_detectors(mock_metric):
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/findMatchingByTags",
            json=FIND_BY_MATCHING_TAGS_MOCK_RESPONSE,
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=47a0661d-aceb-4ef2-bf06-0828f28631b4",
            json=MOCK_DETECTORS[1],
            status=200)
    def validate_update_request(request):
        payload = json.loads(request.body)
        thresholds = payload["detectorConfig"]["params"]["thresholds"]
        assert isclose(thresholds["upperWeak"], 21.19, rel_tol=0.01)
        assert isclose(thresholds["upperStrong"], 26.30, rel_tol=0.01)
        assert isclose(thresholds["lowerWeak"], -9.48, rel_tol=0.01)
        assert isclose(thresholds["lowerStrong"], -14.59, rel_tol=0.01)
        return (200, {}, None)
    responses.add_callback(responses.PUT, "http://modelservice/api/v2/detectors?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            callback=validate_update_request)
    test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    assert len(test_metric.detectors) == 2
    trained_detectors = test_metric.train_detectors()
    assert len(trained_detectors) == 1


@responses.activate
def test_new_untrusted_metric_detector():
    # TODO: graphite returns insufficient data
    pass

@responses.activate
def test_update_untrusted_metric_detector_to_trusted():
    # TODO: graphite returns insufficient data
    pass
    
@responses.activate
def test_update_trusted_metric_to_untrusted():
    # TODO: responses.add model service get detectors for metric (return constant_threshold)
    # TODO: responses.add model service update detector
    pass

@responses.activate
def test_update_trusted_metric_detector():
    # TODO: responses.add model service get detectors for metric (return constant_threshold)
    # TODO: responses.add model service update detector
    pass

@responses.activate
def test_delete_metric():
    # TODO: responses.add model service get detectors for metric (return constant_threshold)
    # TODO: responses.add model service update detector
    pass