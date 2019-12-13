import logging
from statistics import stdev
from math import isclose
import pytest

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def test_get_sample_std_dev_for_integers():
    sample = [5, 4, 7, 9, 15, 1, 0]
    assert isclose(sample_std_dev(sample), 5.1130086, rel_tol=0.0001)

def test_get_sample_std_dev_for_floats():
    sample = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(sample_std_dev(sample), 14.015671, rel_tol=0.0001)

#def test_get_sample_std_dev_for_single_value():
#    sample = [35.2]
#    assert isclose(sample_std_dev(sample), 0.00, rel_tol=0.0001)

def test_get_sample_std_dev_raises_error_with_empty_list():
    with pytest.raises(Exception) as exception:
        assert isclose(sample_std_dev([]), 0)
        assert str(exception.val) == "sample must have at least one element"


################################################################################
## implementation
################################################################################

def sample_std_dev(sample):
    if len(sample) < 1:
        raise Exception("Sample must have at least one element")
    return stdev(sample)

