from adaptive_alerting_detector_build.metrics import Metric
from adaptive_alerting_detector_build.config import MODEL_SERVICE_URL
from adaptive_alerting_detector_build.detectors import Detector
from adaptive_alerting_detector_build.detectors.client import DetectorClient
from adaptive_alerting_detector_build.detectors.mapping import DetectorMapping
import pandas as pd
import pytest
import related
import responses
import json
from tests.conftest import DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE, MOCK_DETECTORS

# @pytest.mark.integration
# @pytest.mark.skipif(MODEL_SERVICE_URL is None)
# def test_detector_client_create_detector(mock_metric):
#     test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
#     assert len(test_metric.metric_detectors) == 0




@responses.activate
def test_detector_client_get_detector(mock_metric):
    responses.add(responses.GET, "http://modelservice/api/v3/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
            json=MOCK_DETECTORS[0],
            status=200)
    detector_client = DetectorClient()
    test_detector = detector_client.get_detector("4fdc3395-e969-449a-a306-201db183c6d7")
    assert isinstance(test_detector, Detector)
    assert test_detector.uuid == "4fdc3395-e969-449a-a306-201db183c6d7"


@responses.activate
def test_detector_list_detector_mappings():
    responses.add(responses.POST, "http://modelservice/api/detectorMappings/search",
            json=[DETECTOR_MAPPINGS_SEARCH_MOCK_RESPONSE[0]],
            status=200)
    detector_client = DetectorClient()
    detector_mappings = detector_client.list_detector_mappings("4fdc3395-e969-449a-a306-201db183c6d7")
    assert isinstance(detector_mappings,list)
    assert len(detector_mappings) == 1
    assert isinstance(detector_mappings[0], DetectorMapping)
    detector_mapping = detector_mappings[0]
    assert detector_mapping.id == "5XeANXABlK1-eG-Fo78V"




# @responses.activate
# def test_detector_client_get_detector(mock_metric):
#     responses.add(responses.POST, "http://modelservice/api/v2/detectors",
#             body="4fdc3395-e969-449a-a306-201db183c6d7",
#             status=201)
#     responses.add(responses.GET, "http://modelservice/api/v2/detectors/findByUuid?uuid=4fdc3395-e969-449a-a306-201db183c6d7",
#             json=MOCK_DETECTORS[0],
#             status=200)
#     detector_client = DetectorClient()
#     test_detector = 
#     test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
#     created_detector = detector_client.create_detector(test_detector, test_metric)

#     detector_client.save_metric_detector_mapping(created_detector.uuid, test_metric)

# @responses.activate
# def test_update_untrusted_metric_detector_to_trusted():
#     # TODO: graphite returns insufficient data
#     pass
    
# @responses.activate
# def test_update_trusted_metric_to_untrusted():
#     # TODO: responses.add model service get detectors for metric (return constant_threshold)
#     # TODO: responses.add model service update detector
#     pass

# @responses.activate
# def test_update_trusted_metric_detector():
#     # TODO: responses.add model service get detectors for metric (return constant_threshold)
#     # TODO: responses.add model service update detector
#     pass

# @responses.activate
# def test_delete_metric():
#     # TODO: responses.add model service get detectors for metric (return constant_threshold)
#     # TODO: responses.add model service update detector
#     pass