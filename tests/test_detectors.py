from adaptive_alerting_detector_build.metrics import Metric
from adaptive_alerting_detector_build.detectors.mapping import DetectorMapping, build_metric_detector_mapping


# def test_build_detector(mock_metric):
    # test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    # metric_detector_mapping=build_metric_detector_mapping("0bc40dd7-7294-42c7-b06a-ca210c3fbf3a",test_metric)
    # assert isinstance(metric_detector_mapping, DetectorMapping)


def test_build_metric_detector_mapping(mock_metric):
    test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    metric_detector_mapping=build_metric_detector_mapping("0bc40dd7-7294-42c7-b06a-ca210c3fbf3a",test_metric)
    assert isinstance(metric_detector_mapping, DetectorMapping)

