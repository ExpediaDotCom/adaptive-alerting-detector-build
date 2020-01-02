from pandas import read_csv
from adaptivealerting.metric_profiler import build_profile


def test_build_profile_stationary():
    series = read_csv("tests/data/daily-total-female-births.csv", header=0, index_col=0, squeeze=True)
    x = series.values
    profile = build_profile(x)
    assert profile["stationary"]


def test_build_profile_nonstationary():
    series = read_csv("tests/data/international-airline-passengers.csv", header=0, index_col=0, squeeze=True)
    x = series.values
    profile = build_profile(x)
    assert not profile["stationary"]
