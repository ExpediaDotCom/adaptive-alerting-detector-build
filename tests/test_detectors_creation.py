import logging
from statistics import pstdev
from math import isclose
import pytest

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def test_get_population_std_dev_for_integers():
    population = [5, 4, 7, 9, 15, 1, 0]
    assert isclose(population_std_dev(population), 4.733726, rel_tol=0.0001)

def test_get_population_std_dev_for_floats():
    population = [35.2, 42.9, 37.8, 9.3, 15.0, 10.1, 20]
    assert isclose(population_std_dev(population), 12.97599, rel_tol=0.0001)

def test_get_population_std_dev_for_single_value():
    population = [35.2]
    assert isclose(population_std_dev(population), 0.00, rel_tol=0.0001)

def test_get_population_std_dev_raises_error_with_empty_list():
    with pytest.raises(Exception) as exception:
        assert isclose(population_std_dev([]), 0)
        assert str(exception.val) == "Population must have at least one element"


################################################################################
## implementation
################################################################################

def population_std_dev(population):
    if len(population) < 1:
        raise Exception("Population must have at least one element")
    return pstdev(population)

