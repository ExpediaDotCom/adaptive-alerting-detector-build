import logging

from pandas import DataFrame

from .stationarity_annotator import annotate_stationarity
from .stationarity_checker import (
    stationarity_check,
    DEFAULT_SIGNIFICANCE,
    DEFAULT_MAX_ADF_PVALUE,
)
from .stationarity_display import print_stationarity_report
from .stationarity_types import StationarityResult, StationarityReport

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# TODO this method and file is specialised for stationarity test, consider preferred using a single point of call
#  and useing build_profile as an entry point for the profiler. We can pass the parameter to select the type of profiler
#  we want to run, like create a stationarity profiler object handler and call the function, something like creating
#  factory methods for object type based on _is_stationary or _is_seasonal. From there handler can call appropriate
#  profiler test function. For stationarity profiler object, it will call _is_stationary and for seasonal profiler
#  object, it can call _is_seasonal.

def build_profile(
    df: DataFrame,
    significance=DEFAULT_SIGNIFICANCE,
    max_adf_pvalue=DEFAULT_MAX_ADF_PVALUE,
    freq: int = None,
    lags: str = None,
):
    """
    Builds a feature profile of the given time series.

    :param df: Pandas DataFrame with DateTimeIndex
    :param significance: The adfuller significance result to be used for test. Valid values are "1%", "5%" and "10%"
    :param max_adf_pvalue: Augmented Dicker-Fuller test result must be less than or equal to this number
    :param freq: Frequency string such as '1D' for 1 day, '5T' for 5 minutes, etc.
                 See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
                 If None is provided, df.index must be of time Datetimestamp, freq will then be derived from either
                 df.index.freq or the timestamps in df.index
    :param lags: The number of lags that should be checked for unit root (i.e. is non-stationary).
                 If None, defaults to number of observations per day (which is derived from the frequency observed in
                 timestamps in provided df)
    :return: boolean indicating whether the time series is stationary, assuming the given significance level
    :return: Timeseries feature profile
    """
    stationarity_result: bool = _is_stationary(
        df=df,
        significance=significance,
        max_adf_pvalue=max_adf_pvalue,
        freq=freq,
        lags=lags,
    )
    return {"stationary": stationarity_result}


def _is_stationary(
    df: DataFrame,
    significance: str,
    max_adf_pvalue: float,
    freq: int = None,
    lags: str = None,
) -> bool:
    """
    Runs a stationarity test on the time series.

    :param df: Pandas DataFrame with DateTimeIndex
    :param significance: The adfuller significance result to be used for test. Valid values are "1%", "5%" and "10%"
    :param max_adf_pvalue: Augmented Dicker-Fuller test result must be less than or equal to this number
    :param freq: Frequency string such as '1D' for 1 day, '5T' for 5 minutes, etc.
                 See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
                 If None is provided, df.index must be of time Datetimestamp, freq will then be derived from either
                 df.index.freq or the timestamps in df.index
    :param lags: The number of lags that should be checked for unit root (i.e. is non-stationary).
                 If None, defaults to number of observations per day (which is derived from the frequency observed in
                 timestamps in provided df)
    :return: boolean indicating whether the time series is stationary, assuming the given significance level
    """
    stationarity_result: StationarityResult = _try_stationarity_check(
        df=df,
        max_adf_pvalue=max_adf_pvalue,
        significance=significance,
        freq=freq,
        lags=lags,
    )
    stationarity_report: StationarityReport = _build_stationarity_report(
        stationarity_result, significance, max_adf_pvalue
    )
    print_stationarity_report(stationarity_report)
    return stationarity_result.is_stationary


def _try_stationarity_check(
    df, max_adf_pvalue: float, significance: str, freq: int = None, lags: str = None
) -> StationarityResult:
    try:
        return stationarity_check(
            df=df,
            freq=freq,
            max_adf_pvalue=max_adf_pvalue,
            significance=significance,
            lags=lags,
        )
    except Exception as e:
        raise ValueError("Encountered error during analysis") from e


def _build_stationarity_report(stationarity_result, significance, max_adf_pvalue):
    test_stat = stationarity_result.adf_result.adfstat
    p_value = stationarity_result.adf_result.pvalue
    crit_value = stationarity_result.adf_result.critvalues[significance]
    LOGGER.info(
        f"\ncritvalue[{significance}]={crit_value}, test_stat={test_stat}, p_value={p_value}"
    )
    stationarity_report: StationarityReport = annotate_stationarity(
        stationarity_result, significance=significance, max_adf_pvalue=max_adf_pvalue
    )
    return stationarity_report
