"""Tests for Detectors Builders module."""

from math import isclose
from re import search
import pytest
from adaptive_alerting_detector_build.detectors import create_detector
from adaptive_alerting_detector_build.detectors.constant_threshold import (
    ConstantThresholdStrategy,
)
from adaptive_alerting_detector_build.detectors import exceptions
from adaptive_alerting_detector_build.metrics import metric
from .fixtures import mock_metric
import responses
import json


@pytest.mark.detectors
class TestDetectors:

    # def test_calculate_sigma_for_integers(self):
    #     sample = [5, 4, 7, 9, 15, 1, 0]
    #     assert isclose(ct._calculate_sigma(sample), 5.1130086, rel_tol=0.0001)

    # def test_calculate_sigma_for_floats(self):
    #     sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    #     assert isclose(ct._calculate_sigma(sample), 14.015671, rel_tol=0.0001)

    # def test_calculate_sigma_raises_error_for_single_value(self):
    #     sample = [35.2]
    #     with pytest.raises(exceptions.DetectorBuilderError) as exception:
    #         assert isclose(ct._calculate_sigma(sample), 0)
    #     assert str(exception.value) == "Sample must have at least two elements"

    # def test_calculate_sigma_raises_error_with_empty_list(self):
    #     with pytest.raises(exceptions.DetectorBuilderError) as exception:
    #         assert isclose(ct._calculate_sigma([]), 0)
    #     assert str(exception.value) == "Sample must have at least two elements"

    # def test_calculate_mean_for_floats(self):
    #     sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    #     assert isclose(ct._calculate_mean(sample), 24.328571, rel_tol=0.0001)

    # def test_calculate_mean_for_single_value(self):
    #     sample = [35.2]
    #     assert isclose(ct._calculate_mean(sample), 35.2, rel_tol=0.0001)

    # def test_calculate_sigma_thresholds(self):
    #     sigma = 5
    #     mean = 10
    #     multiplier = 3
    #     upper, lower = ct._calculate_sigma_thresholds(sigma, mean, multiplier)
    #     assert upper == 25   # 10 + 5 * 3; mean + sigma * multiplier
    #     assert lower == -5   # 10 - 5 * 3; mean - sigma * multiplier

    # def test_calculate_quartiles(self):
    #     sample = [2, 5, 6, 7, 10, 22, 13, 14, 16, 65, 45, 12]
    #     q1, median, q3 = ct._calculate_quartiles(sample)
    #     assert q1 == 6.5
    #     assert median == 12.5
    #     assert q3 == 19.0

    # def test_calculate_quartiles_for_single_value(self):
    #     sample = [2]
    #     q1, median, q3 = ct._calculate_quartiles(sample)
    #     assert q1 == 2
    #     assert median == 2
    #     assert q3 == 2

    # def test_calculate_quartile_thresholds(self):
    #     q1, q3 = 2, 5
    #     multiplier = 1.5
    #     upper, lower = ct._calculate_quartile_thresholds(q1, q3, multiplier)
    #     assert upper == 9.5 # (q3 + (q3 - q1) * 1.5)
    #     assert lower == -2.5 # (q1 - (q3 - q1) * 1.5)

    def test_create_detector_with_sigma_strategy(self):
        detector_config = dict(
            training_metadata=dict(
                strategy="sigma", weak_multiplier=3.0, strong_multiplier=5.0
            )
        )
        test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
        test_detector = create_detector("constant_threshold", detector_config)
        data = test_metric.query()
        test_detector.train(data)
        print("test_detector.config.training_metadata.strategy", test_detector.config.training_metadata.strategy)
        assert (
            test_detector.config.training_metadata.strategy
            == ConstantThresholdStrategy.SIGMA
        )
        assert isclose(
            test_detector.config.hyperparameters.weak_upper_threshold,
            21.196168,
            rel_tol=0.0001,
        )
        assert isclose(
            test_detector.config.hyperparameters.strong_upper_threshold,
            31.422185,
            rel_tol=0.0001,
        )
        assert isclose(
            test_detector.config.hyperparameters.weak_lower_threshold,
            -9.481883,
            rel_tol=0.0001,
        )
        assert isclose(
            test_detector.config.hyperparameters.strong_lower_threshold,
            -19.70790,
            rel_tol=0.0001,
        )

    def test_create_detector_with_quartile_strategy(self, mock_metric):
        detector_config = dict(
            strategy="quartile", weak_multiplier=1.5, strong_multiplier=3.0
        )
        test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
        test_detector = ConstantThresholdDetector(test_metric, detector_config)
        data = test_metric.query()
        test_detector.train(data)
        assert (
            test_detector.config.training_metadata.strategy
            == ConstantThresholdStrategy.QUARTILE
        )
        assert test_detector.config.hyperparameters.weak_upper_threshold == 16.25
        assert test_detector.config.hyperparameters.strong_upper_threshold == 24.5
        assert test_detector.config.hyperparameters.weak_lower_threshold == -5.75
        assert test_detector.config.hyperparameters.strong_lower_threshold == -14

    # def test_create_detector_with_invalid_strategy_raises_build_error(
    #     self, mock_metric
    # ):
    #     detector_config = dict(
    #         strategy="invalid strategy", weak_multiplier=3, strong_multiplier=5
    #     )
    #     test_metric = mock_metric()
    #     with pytest.raises(ValueError) as exception:
    #         test_detector = ConstantThresholdDetector(test_metric, detector_config)
    #     assert (
    #         str(exception.value)
    #         == "'invalid strategy' is not a valid constant_threshold_strategy"
    #     )

    # def test_train_detector_with_invalid_sample_size_raises_build_error(
    #     self, mock_metric
    # ):
    #     detector_config = dict(strategy="sigma", weak_multiplier=3, strong_multiplier=5)
    #     test_metric = mock_metric(data=[3])
    #     test_detector = ConstantThresholdDetector(test_metric, detector_config)
    #     data = test_metric.query()
    #     with pytest.raises(exceptions.DetectorBuilderError) as exception:
    #         test_detector.train(data)
    #     assert str(exception.value) == "Sample must have at least two elements"
