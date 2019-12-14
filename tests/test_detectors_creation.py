import logging
from math import isclose
import pytest
import numpy as np

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def test_get_sample_std_dev_for_integers():
    sample = [5, 4, 7, 9, 15, 1, 0]
    assert isclose(sample_std_dev(sample), 5.1130086, rel_tol=0.0001)

def test_get_sample_std_dev_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(sample_std_dev(sample), 14.015671, rel_tol=0.0001)

def test_get_sample_std_dev_raises_error_for_single_value():
    sample = [35.2]
    with pytest.raises(Exception) as exception:
        assert isclose(sample_std_dev(sample), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_get_sample_std_dev_raises_error_with_empty_list():
    with pytest.raises(Exception) as exception:
        assert isclose(sample_std_dev([]), 0)
    assert str(exception.value) == "Sample must have at least two elements"

def test_calculate_quartiles_without_multipliers():
    sample = [2, 5, 6, 7, 10, 22, 13, 14, 16, 65, 45, 12]
    q1, median, q3 = calculate_quartiles(sample)
    assert q1 == 6.5
    assert median == 12.5
    assert q3 == 19.0


################################################################################
## implementation
################################################################################

def sample_std_dev(sample):
    if len(sample) < 2:
        raise Exception("Sample must have at least two elements")
    array = np.array(sample)
    return np.std(array, ddof=1)

def calculate_quartiles(sample):
    array = np.array(sample)
    return np.percentile(array, [25, 50, 75], interpolation='midpoint')
