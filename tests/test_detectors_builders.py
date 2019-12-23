"""Tests for Detectors Builders module."""

from math import isclose
import pytest
from adaptivealerting.detectors.builders import constant_threshold as ct

def test_calculate_sigma_for_integers():
    sample = [5, 4, 7, 9, 15, 1, 0]
    assert isclose(ct.calculate_sigma(sample), 5.1130086, rel_tol=0.0001)

def test_calculate_sigma_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(ct.calculate_sigma(sample), 14.015671, rel_tol=0.0001)

def test_calculate_sigma_raises_error_for_single_value():
    sample = [35.2]
    with pytest.raises(Exception) as exception:
        assert isclose(ct.calculate_sigma(sample), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_sigma_raises_error_with_empty_list():
    with pytest.raises(Exception) as exception:
        assert isclose(ct.calculate_sigma([]), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_mean_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(ct.calculate_mean(sample), 24.328571, rel_tol=0.0001)

def test_calculate_mean_for_single_value():
    sample = [35.2]
    assert isclose(ct.calculate_mean(sample), 35.2, rel_tol=0.0001)

def test_calculate_sigma_thresholds():
    sigma = 5
    mean = 10
    multiplier = 3
    upper, lower = ct.calculate_sigma_thresholds(sigma, mean, multiplier)
    assert upper == 25   # 10 + 5 * 3; mean + sigma * multiplier
    assert lower == -5   # 10 - 5 * 3; mean - sigma * multiplier

def test_calculate_quartiles():
    sample = [2, 5, 6, 7, 10, 22, 13, 14, 16, 65, 45, 12]
    q1, median, q3 = ct.calculate_quartiles(sample)
    assert q1 == 6.5
    assert median == 12.5
    assert q3 == 19.0

def test_calculate_quartiles_for_single_value():
    sample = [2]
    q1, median, q3 = ct.calculate_quartiles(sample)
    assert q1 == 2
    assert median == 2
    assert q3 == 2

def test_calculate_quartile_thresholds():
    q1, q3 = 2, 5
    multiplier = 1.5
    upper, lower = ct.calculate_quartile_thresholds(q1, q3, multiplier)
    assert upper == 9.5 # (q3 + (q3 - q1) * 1.5)
    assert lower == -2.5 # (q1 - (q3 - q1) * 1.5)

def test_create_detector_with_sigma_strategy():
    sample = [5, 4, 7, 9, 15, 1, 0]
    weak_multiplier = 3
    strong_multiplier = 5
    ct_builder = ct.ConstantThresholdDetectorBuilder()
    detector = ct_builder.detector(ct_builder.Strategy.SIGMA, sample, weak_multiplier,
                                       strong_multiplier)
    assert detector.build_strategy == ct_builder.Strategy.SIGMA
    assert isclose(detector.weak_upper_threshold, 21.196168, rel_tol=0.0001)
    assert isclose(detector.strong_upper_threshold, 31.422185, rel_tol=0.0001)
    assert isclose(detector.weak_lower_threshold, -9.481883, rel_tol=0.0001)
    assert isclose(detector.strong_lower_threshold, -19.70790, rel_tol=0.0001)

def test_create_detector_with_quartile_strategy():
    sample = [5, 4, 7, 9, 15, 1, 0]
    weak_multiplier = 1.5
    strong_multiplier = 3.0
    ct_builder = ct.ConstantThresholdDetectorBuilder()
    detector = ct_builder.detector(ct_builder.Strategy.QUARTILE, sample, weak_multiplier,
                                       strong_multiplier)
    assert detector.build_strategy == ct_builder.Strategy.QUARTILE
    assert detector.weak_upper_threshold == 16.25
    assert detector.strong_upper_threshold == 24.5
    assert detector.weak_lower_threshold == -5.75
    assert detector.strong_lower_threshold == -14

#TODO: test exception for invalid sample
