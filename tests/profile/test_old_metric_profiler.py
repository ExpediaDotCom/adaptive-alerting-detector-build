import pytest

from adaptive_alerting_detector_build.profile.old_metric_profiler import old_build_profile
from tests.csv_helper import read_timeseries_csv

# This is superseded by test_metric_profiler.py.
# TODO: Remove this file once comparison with old and new profiler output is complete
def test_build_profile_stationary():
    df = read_timeseries_csv("tests/data/daily-total-female-births.csv")
    profile = old_build_profile(df)
    assert profile["stationary"]


def test_build_profile_stationary_diff_goog200():
    df = read_timeseries_csv("tests/data/diff_goog200.csv")
    profile = old_build_profile(df)
    assert profile["stationary"]


def test_build_profile_nonstationary():
    df = read_timeseries_csv("tests/data/international-airline-passengers.csv")
    profile = old_build_profile(df)
    assert not profile["stationary"]


def test_build_profile_nonstationary_goog200():
    df = read_timeseries_csv("tests/data/goog200.csv")
    profile = old_build_profile(df)
    assert not profile["stationary"]


# This test demonstrates the adfuller issue that metric_profiler resolves.
@pytest.mark.xfail
def test_build_profile_nonstationary_reproduce_issue():
    # This dataset is non-stationary but profiler reports
    df = read_timeseries_csv("tests/data/complex_nonstationary.csv")
    df.fillna(0, inplace=True)
    profile = old_build_profile(df)
    # This assertion should pass:
    assert not profile["stationary"]
