"""Tests for CTHighwatermark Detectors Builders module."""

from math import isclose
import pytest
import related
import json
import pandas
import numpy as np

from adaptive_alerting_detector_build.detectors import build_detector, DetectorClient
from adaptive_alerting_detector_build.detectors import Detector
from pandas import read_csv

from adaptive_alerting_detector_build.detectors import (
    exceptions,
    constant_threshold as ct,
)


@pytest.mark.highwatermarkdetectors
class TestCTHighwatermarkDetector:
    def test_train_detector_for_latency_a(self):
        detector_config = dict(
            hyperparams=dict(upper_weak_multiplier=1.05, upper_strong_multiplier=1.10, 
                hampel_window_size=10, hampel_n_sigma=3, strategy="highwatermark")
        )
        detector_class = build_detector("constant-detector", detector_config)
        data = read_csv("./tests/data/latency_test_a.csv", header=0, usecols=[1], squeeze=True)
        detector_class.train(data, "LATENCY")
        print("detector model data after training:\n", related.to_json(detector_class))
        assert isclose(detector_class.config.params.thresholds.strong_upper_threshold, 43711.030462, rel_tol=0.0001)
        assert isclose(detector_class.config.params.thresholds.weak_upper_threshold, 41724.165441, rel_tol=0.0001)

    def test_train_detector_for_latency_b(self):
        detector_config = dict(
            hyperparams=dict(upper_weak_multiplier=1.05, upper_strong_multiplier=1.10, 
                hampel_window_size=10, hampel_n_sigma=3, strategy="highwatermark")
        )
        detector_class = build_detector("constant-detector", detector_config)
        data = read_csv("./tests/data/latency_test_b.csv", header=0, usecols=[1], squeeze=True)
        detector_class.train(data, "LATENCY")
        print("detector model data after training:\n", related.to_json(detector_class))
        assert isclose(detector_class.config.params.thresholds.strong_upper_threshold, 0.612911, rel_tol=0.0001)
        assert isclose(detector_class.config.params.thresholds.weak_upper_threshold, 0.585052, rel_tol=0.0001)

    def test_data_raises_error_with_empty_list_a(self):
        with pytest.raises(exceptions.DetectorBuilderError) as exception:
            ct._data_cleanup(pandas.Series([]))
        assert str(exception.value) == "Sample must have at least thirty elements"
    
    def test_data_raises_error_with_empty_list_b(self):
        with pytest.raises(exceptions.DetectorBuilderError) as exception:
            ct._hampel_filter(np.array([], dtype=np.float64))
        assert str(exception.value) == "Sample must have at least thirty elements"
