"""Tests for Detectors Builders module."""

from math import isclose
from re import search
import pytest
from adaptive_alerting_detector_build.detectors import build_detector
from adaptive_alerting_detector_build.detectors.constant_threshold import (
    ConstantThresholdStrategy, ConstantThresholdConfig
)
from adaptive_alerting_detector_build.detectors import exceptions, constant_threshold as ct
from adaptive_alerting_detector_build.metrics import metric
import responses
import related
import json

from tests.conftest import FIND_BY_MATCHING_TAGS_EMPTY_MOCK_RESPONSE, MOCK_DETECTORS


def test_calculate_sigma_for_integers():
    sample = [5, 4, 7, 9, 15, 1, 0]
    assert isclose(ct._calculate_sigma(sample), 5.1130086, rel_tol=0.0001)

def test_calculate_sigma_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(ct._calculate_sigma(sample), 14.015671, rel_tol=0.0001)

def test_calculate_sigma_raises_error_for_single_value():
    sample = [35.2]
    with pytest.raises(exceptions.DetectorBuilderError) as exception:
        assert isclose(ct._calculate_sigma(sample), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_sigma_raises_error_with_empty_list():
    with pytest.raises(exceptions.DetectorBuilderError) as exception:
        assert isclose(ct._calculate_sigma([]), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_mean_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(ct._calculate_mean(sample), 24.328571, rel_tol=0.0001)

def test_calculate_mean_for_single_value():
    sample = [35.2]
    assert isclose(ct._calculate_mean(sample), 35.2, rel_tol=0.0001)

# def test_calculate_sigma_thresholds():
#     sigma = 5
#     mean = 10
#     multiplier = 3
#     upper, lower = ct._calculate_sigma_thresholds(sigma, mean, multiplier)
#     assert upper == 25   # 10 + 5 * 3; mean + sigma * multiplier
#     assert lower == -5   # 10 - 5 * 3; mean - sigma * multiplier

def test_calculate_quartiles():
    sample = [2, 5, 6, 7, 10, 22, 13, 14, 16, 65, 45, 12]
    q1, median, q3 = ct._calculate_quartiles(sample)
    assert q1 == 6.5
    assert median == 12.5
    assert q3 == 19.0

def test_calculate_quartiles_for_single_value():
    sample = [2]
    q1, median, q3 = ct._calculate_quartiles(sample)
    assert q1 == 2
    assert median == 2
    assert q3 == 2

# def test_calculate_quartile_thresholds():
#     q1, q3 = 2, 5
#     multiplier = 1.5
#     upper, lower = ct._calculate_quartile_thresholds(q1, q3, multiplier)
#     assert upper == 9.5 # (q3 + (q3 - q1) * 1.5)
#     assert lower == -2.5 # (q1 - (q3 - q1) * 1.5)

def test_load_constant_threshold_config():
    detector_config = dict(
        hyperparams=dict(
            strategy="sigma", weak_multiplier=3.0, strong_multiplier=5.0
        )
    )
    constant_threshold_config = related.to_model(ConstantThresholdConfig, detector_config)
    assert isinstance(constant_threshold_config, ConstantThresholdConfig)

def test_build_detector_with_sigma_strategy(mock_metric):
    detector_config = dict(
        hyperparams=dict(
            strategy="sigma", 
            upper_weak_multiplier=3.0, 
            upper_strong_multiplier=5.0,
            lower_weak_multiplier=3.0, 
            lower_strong_multiplier=5.0
        )
    )
    test_metric = mock_metric(data=[5, 4, 7, 9, 15, 1, 0])
    test_detector = build_detector("constant-detector", detector_config)
    data = test_metric.query()
    test_detector.train(data)
    assert (
        test_detector.config.hyperparams.strategy
        == ConstantThresholdStrategy.SIGMA
    )
    assert isclose(
        test_detector.config.params.thresholds.weak_upper_threshold,
        21.196168,
        rel_tol=0.0001,
    )
    assert isclose(
        test_detector.config.params.thresholds.strong_upper_threshold,
        31.422185,
        rel_tol=0.0001,
    )
    assert isclose(
        test_detector.config.params.thresholds.weak_lower_threshold,
        -9.481883,
        rel_tol=0.0001,
    )
    assert isclose(
        test_detector.config.params.thresholds.strong_lower_threshold,
        -19.70790,
        rel_tol=0.0001,
    )

def test_build_detector_with_quartile_strategy(mock_metric):
    detector_config = dict(
        hyperparams =dict(
            strategy="quartile", 
            lower_weak_multiplier=1.5, 
            lower_strong_multiplier=3.0,
            upper_weak_multiplier=1.5, 
            upper_strong_multiplier=3.0,
        )
    )
    test_metric = mock_metric(data=[5, 4, 7, 9, 15, None, 1, 0])
    test_detector = build_detector("constant-detector", detector_config)
    data = test_metric.query()
    test_detector.train(data)
    assert (
        test_detector.config.hyperparams.strategy
        == ConstantThresholdStrategy.QUARTILE
    )
    assert test_detector.config.params.thresholds.weak_upper_threshold == 16.25
    assert test_detector.config.params.thresholds.strong_upper_threshold == 24.5
    assert test_detector.config.params.thresholds.weak_lower_threshold == -5.75
    assert test_detector.config.params.thresholds.strong_lower_threshold == -14

def test_build_detector_with_invalid_strategy_raises_build_error(mock_metric):
    detector_config = dict(
        hyperparams =dict(
            strategy="invalid strategy", weak_multiplier=1.5, strong_multiplier=3.0
        )
    )
    with pytest.raises(ValueError) as exception:
        build_detector("constant-detector", detector_config)
    assert "'invalid strategy' is not a valid ConstantThresholdStrategy" in str(exception.value)


@responses.activate
def test_train_detector_with_invalid_sample_size_raises_build_error(mock_metric):
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
    test_metric = mock_metric(data=[3])
    with pytest.raises(exceptions.DetectorBuilderError) as exception:
        test_metric.build_detectors()
    assert str(exception.value) == "Sample must have at least two elements"