import datetime
from datetime import timedelta

import pandas as pd
from pandas import DatetimeIndex, DataFrame, Series
import logging

from pandas._libs.tslibs.timedeltas import Timedelta

LOGGER = logging.getLogger(__name__)

# TODO: Move this module to a shared package - i.e. it is not profile-specific

def obs_per_day(df, freq_override=None):
    """
    Calculates the number of observations per day.
    :param df: Pandas DataFrame with DateTimeIndex
    :param freq_override: Explicit frequency to use in cases where provided df does not have a DateTimeIndex index
    :return: Number of observations per day or 0 if freq (derived or overridden) is > 1 day
    """
    if freq_override:
        if type(freq_override == str):
            result = calculate_obs_per_day_for_str_freq(freq_override)
            print(f"Using provided freq_override '{freq_override}'. This means we expect {result} observations per day.")
        else:
            raise ValueError(f"Unsupported freq_override type {type(freq_override)}. Please use a string. See "
                             f"https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases")
    else:
        if type(df.index) == DatetimeIndex:
            result = obs_per_day_for_datetimeindex(df)
        else:
            raise ValueError(f"Must provide a 'freq_override' parameter when df.index type ({type(df.index).__name__}) "
                             f"is not DatetimeIndex")
    print(f"Provided data (with a total of {len(df)} data points) contains {result} observations per day.")
    return result


def calculate_obs_per_day_for_str_freq(freq_str):
    """
    :param freq_str: Frequency string such as '1D' for 1 day, '5T' for 5 minutes, etc.
                     See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    :return: Number of observations per day at given freq
    """
    now = datetime.datetime.now()
    plus1w = now + pd.DateOffset(1)
    index = pd.date_range(now, plus1w, freq=freq_str)
    series = pd.Series(range(len(index)), index=index)
    return len(series) - 1


def obs_per_day_for_datetimeindex(df):
    index_freq = df.index.freq
    if index_freq:
        freq_as_timedelta = pd.to_timedelta(index_freq)
        print(f"Data provided has an index of type '{type(index_freq).__name__}' with a freq of {index_freq} "
              f"(timedelta: {freq_as_timedelta})")
    else:
        freq_as_timedelta = (df.index[1] - df.index[0])  # Timedelta representing distance between first two observations
        print(f"Data provided has no index. Using the first two data points, we've derived a frequency timedelta of "
              f"'{freq_as_timedelta}'.")
    if freq_as_timedelta > timedelta(days=1):
        return 0
    s: Series = resample_first_day(df, freq_as_timedelta)
    return len(s) - 1


def resample_first_day(df: DataFrame, freq_as_timedelta: Timedelta) -> Series:
    """
    Takes the provided DataFrame and resamples the values using the provided freq_as_timedelta.
    This can be used to calculate number of observations per day the freq_as_timedelta gives.
    :param df: Pandas DataFrame with index of type DatetimeIndex
    :param freq_as_timedelta: Pandas Timedelta
    :return: Pandas Series
    """
    first_two_timestamps = [df.index[0], df.index[0] + pd.DateOffset(1)]
    dti: DatetimeIndex = pd.to_datetime(first_two_timestamps)
    s = pd.Series(0, index=dti)
    return s.resample(freq_as_timedelta).last()


def df_values_as_array(df):
    return df.iloc[:, 0].values


def convert_df_to_str(df: pd.DataFrame):
    as_str = str(df)
    return as_str[:as_str.rfind('\n')]  # Remove 'dtype float64' last line of tabular string represenation
