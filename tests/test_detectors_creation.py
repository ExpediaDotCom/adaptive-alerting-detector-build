import logging
from math import isclose
import pytest
import numpy as np

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def test_calculate_sigma_for_integers():
    sample = [5, 4, 7, 9, 15, 1, 0]
    assert isclose(calculate_sigma(sample), 5.1130086, rel_tol=0.0001)

def test_calculate_sigma_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(calculate_sigma(sample), 14.015671, rel_tol=0.0001)

def test_calculate_sigma_raises_error_for_single_value():
    sample = [35.2]
    with pytest.raises(Exception) as exception:
        assert isclose(calculate_sigma(sample), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_sigma_raises_error_with_empty_list():
    with pytest.raises(Exception) as exception:
        assert isclose(calculate_sigma([]), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_mean_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(calculate_mean(sample), 24.328571, rel_tol=0.0001)

def test_calculate_mean_for_single_value():
    sample = [35.2]
    assert isclose(calculate_mean(sample), 35.2, rel_tol=0.0001)

def test_calculate_sigma_thresholds():
    sigma = 5
    mean = 10
    multiplier = 3
    upper, lower = calculate_sigma_thresholds(sigma, mean, multiplier)
    assert upper == 25   # 10 + 5 * 3; mean + sigma * multiplier
    assert lower == -5   # 10 - 5 * 3; mean - sigma * multiplier

def test_calculate_quartiles():
    sample = [2, 5, 6, 7, 10, 22, 13, 14, 16, 65, 45, 12]
    q1, median, q3 = calculate_quartiles(sample)
    assert q1 == 6.5
    assert median == 12.5
    assert q3 == 19.0

def test_calculate_quartiles_for_single_value():
    sample = [2]
    q1, median, q3 = calculate_quartiles(sample)
    assert q1 == 2
    assert median == 2
    assert q3 == 2

def test_calculate_quartile_thresholds():
    q1, q3 = 2, 5
    multiplier = 1.5
    upper, lower = calculate_quartile_thresholds(q1, q3, multiplier)
    assert upper == 9.5 # (q3 + (q3 - q1) * 1.5)
    assert lower == -2.5 # (q1 - (q3 - q1) * 1.5)

# TODO: weak and strong outliers, using provided multiplier
# using sigmas to find outliers
# using percentiles to find outliers


################################################################################
## implementation
################################################################################

def calculate_sigma(sample):
    if len(sample) < 2:
        raise Exception("Sample must have at least two elements")
    array = np.array(sample)
    return np.std(array, ddof=1)

def calculate_mean(sample):
    array = np.array(sample)
    return np.mean(array)

def calculate_sigma_thresholds(sigma, mean, multiplier):
    upper = mean + sigma * multiplier
    lower = mean - sigma * multiplier
    return upper, lower

def calculate_quartiles(sample):
    array = np.array(sample)
    return np.percentile(array, [25, 50, 75], interpolation='midpoint')

def calculate_quartile_thresholds(q1, q3, multiplier):
    iqr = q3 - q1
    upper = q3 + iqr * multiplier
    lower = q1 - iqr * multiplier
    return upper, lower
