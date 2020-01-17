from adaptive_alerting_detector_build.profile.metric_profiler import build_profile
from tests.csv_helper import read_timeseries_csv


def test_build_profile_stationary():
    df = read_timeseries_csv("tests/data/daily-total-female-births.csv")
    profile = build_profile(df)
    assert profile["stationary"]


def test_build_profile_stationary_diff_goog200():
    df = read_timeseries_csv("tests/data/diff_goog200.csv")
    profile = build_profile(df, freq="1d")
    assert profile["stationary"]


def test_build_profile_nonstationary():
    df = read_timeseries_csv("tests/data/international-airline-passengers.csv")
    profile = build_profile(df)
    assert not profile["stationary"]


def test_build_profile_nonstationary_goog200():
    df = read_timeseries_csv("tests/data/goog200.csv")
    profile = build_profile(df, freq="1d")
    assert not profile["stationary"]


def test_build_profile_nonstationary_complex_FailingTest():
    df = read_timeseries_csv("tests/data/complex_nonstationary.csv")
    df.fillna(0, inplace=True)
    from profile.old_metric_profiler import old_build_profile
    profile = old_build_profile(df)
    assert not profile["stationary"]


def test_build_profile_nonstationary_complex():
    df = read_timeseries_csv("tests/data/complex_nonstationary.csv")
    df.fillna(0, inplace=True)
    profile = build_profile(df, significance="1%")
    assert not profile["stationary"]
