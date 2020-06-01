import math
import numpy as np
import pandas as pd
import pytest

from adaptive_alerting_detector_build.profile.seasonal_metric_profiler import build_seasonal_profile
from tests.csv_helper import read_timeseries_csv


def test_build_profile_seasonal():
    # a simple multiplicative sine function
    series = _get_generated_sine_dataset()
    series_df = pd.DataFrame(series, columns=["value"])
    profile = build_seasonal_profile(series_df)
    assert profile["seasonal"]


def test_build_profile_seasonal_noisy():
    # a simple multiplicative sine function with noise
    noisy = _get_generated_noisy_sine_dataset()
    noisy_df = pd.DataFrame(noisy, columns=["value"])
    profile = build_seasonal_profile(noisy_df)
    assert profile["seasonal"]


def test_build_profile_nonseasonal():
    # a simple linear function
    series = [i / 5.0 for i in range(100)]
    series_df = pd.DataFrame(series, columns=["value"])
    profile = build_seasonal_profile(series_df)
    assert not profile["seasonal"]


def test_build_profile_nonseasonal_noisy():
    # a simple linear function with noise
    series = [i / 5.0 for i in range(100)]
    noisy = series + np.random.normal(0, 5, len(series))
    noisy_df = pd.DataFrame(noisy, columns=["value"])
    profile = build_seasonal_profile(noisy_df)
    assert not profile["seasonal"]


def test_build_profile_seasonal_loaded_dataset():
    # dataset from https://www.kaggle.com/rtatman/us-candy-production-by-month?select=candy_production.csv
    series = read_timeseries_csv("tests/data/candy_production.csv")
    profile = build_seasonal_profile(series)
    assert profile["seasonal"]


def test_build_profile_seasonal_with_correct_period():
    # a simple multiplicative sine function
    series = _get_generated_sine_dataset()
    series_df = pd.DataFrame(series, columns=["value"])
    profile = build_seasonal_profile(series_df, period=25)
    assert profile["seasonal"]


def test_build_profile_seasonal_with_wrong_period_argument_lower_than_length_of_season():
    # a simple multiplicative sine function
    series = _get_generated_sine_dataset()
    series_df = pd.DataFrame(series, columns=["value"])
    profile = build_seasonal_profile(series_df, period=17)
    assert not profile["seasonal"]


def test_build_profile_seasonal_with_wrong_period_argument_larger_than__length_of_season():
    # a simple multiplicative sine function
    with pytest.raises(ValueError) as exception:
        series = _get_generated_sine_dataset()
        series_df = pd.DataFrame(series, columns=["value"])
        build_seasonal_profile(series_df, period=2727)
    assert str(exception.value) == "Encountered error during seasonal test"


def test_build_profile_seasonal_empty_dataset():
    with pytest.raises(ValueError) as exception:
        series = []
        series_df = pd.DataFrame(series, columns=["value"])
        profile = build_seasonal_profile(series_df)
        assert profile["seasonal"]
    assert str(exception.value) == "Encountered error during seasonal test"


def _get_generated_sine_dataset():
    return [10 * math.sin(i * 2 * math.pi / 25) + i * i / 100.0 for i in range(100)]


def _get_generated_noisy_sine_dataset():
    series = _get_generated_sine_dataset()
    noisy = series + np.random.normal(0, 5, len(series))
    return noisy
