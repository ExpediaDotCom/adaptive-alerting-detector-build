import datetime

import pandas as pd

import adaptive_alerting_detector_build.profile.df_helper as subject

TEST_DATA_PATH = f"resources/stats_helper"
FREQ_2DAYS = '2D'
FREQ_1DAY = '1D'
FREQ_1HR = '1H'
FREQ_5MIN = '5T'
FREQ_1MIN = '1T'
OBS_PER_DAY_1HR = 24
OBS_PER_DAY_5MIN = (60 / 5) * 24
OBS_PER_DAY_1MIN = 60 * 24


def test_obs_per_day():
    assert OBS_PER_DAY_1HR == subject.obs_per_day(build_one_week_df_with_freq(FREQ_1HR))
    assert OBS_PER_DAY_5MIN == subject.obs_per_day(build_one_week_df_with_freq(FREQ_5MIN))
    assert OBS_PER_DAY_1MIN == subject.obs_per_day(build_one_week_df_with_freq(FREQ_1MIN))
    assert OBS_PER_DAY_5MIN == subject.obs_per_day(build_5mins_df_without_freq())
    assert 1 == subject.obs_per_day(build_one_week_df_with_freq(FREQ_1DAY))
    assert 0 == subject.obs_per_day(build_one_week_df_with_freq(FREQ_2DAYS))


def test_calculate_obs_per_day_for_str_freq1():
    assert 1 == subject.calculate_obs_per_day_for_str_freq('1D')


def test_calculate_obs_per_day_for_str_freq2():
    assert 0 == subject.calculate_obs_per_day_for_str_freq('25H')


def build_one_week_df_with_freq(freq):
    now = datetime.datetime.now()
    plus1w = now + pd.DateOffset(7)
    index = pd.date_range(now, plus1w, freq=freq)
    series = pd.Series(range(len(index)), index=index)
    return pd.DataFrame(series)


def build_5mins_df_without_freq():
    now = datetime.datetime.now()
    plus5min = datetime.timedelta(minutes=5)
    index = pd.to_datetime([now, now + plus5min])
    print(f"index: {index}")
    series = pd.Series(range(len(index)), index=index)
    return pd.DataFrame(series, index)
