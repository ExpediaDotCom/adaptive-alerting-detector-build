from pandas import read_csv
from adaptivealerting.metric_profiler.stationarity import is_stationary


def test_is_stationary_true():
    series = read_csv("tests/data/daily-total-female-births.csv", header=0, index_col=0, squeeze=True)
    x = series.values
    assert is_stationary(x, "5%")


def test_is_stationary_false():
    series = read_csv("tests/data/international-airline-passengers.csv", header=0, index_col=0, squeeze=True)
    x = series.values
    assert not is_stationary(x, "5%")
