import logging

import numpy as np
from pandas import DataFrame
from statsmodels.tools.sm_exceptions import MissingDataError
from seasonal import fit_seasons

from .df_helper import df_values_as_array
from .df_helper import obs_per_day
from .seasonality_types import SeasonalityResult
from .stationarity_types import AdfResultWrapper, StationarityResult

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def _preprocess_data(df: DataFrame):
    """
    Interpolate missing values in timeseries.
    First and last values in timeseries can still remain NaN after interpolation,
    therefore replacing them with zeroes.
    :param df: Pandas DataFrame with DateTimeIndex
    :return: numpy data series
    """
    df = df['value']
    df_interpolated = df.interpolate(method='polynomial', order=1)
    df_nonan = df_interpolated.replace(np.nan, 0.0)
    series = df_nonan.to_numpy()
    return series

def seasonality_check(
    df: DataFrame,
        period = None
) -> SeasonalityResult:
    """
    Performs seasonality check in a time series using https://pypi.org/project/seasonal/
    :param df: Pandas DataFrame with DateTimeIndex
    :param period: seasonality period
    :return: SeasonalityResult
    """

    data = _preprocess_data(df)

    print('Running seasionality test...')
    seasons, trend = fit_seasons(data, period=period)

    if seasons is not None:
        period = len(seasons)
    else:
        period = None
    is_seasonal = period is not None
    return SeasonalityResult(is_seasonal=is_seasonal, period=period)


def _adf_stationarity_test(
    df: DataFrame, freq_override: str = None, lags: int = None
) -> AdfResultWrapper:
    """

    :param df: Pandas DataFrame with DateTimeIndex
    :param freq_override: Explicit frequency to use in cases where provided df does not have a DateTimeIndex index
    :param lags: The number of lags that should be checked for unit root (i.e. is non-stationary).
                 If None, defaults to number of observations per day (which is derived from the frequency observed in
                 timestamps in provided df)
    :return: AdfResultWrapper with icbest = None when lags (provided or auto-derived) > AUTO_LAG_THRESHOLD
    """
    series = df_values_as_array(df)
    lags = determine_lags_to_use(df, freq_override, lags)
    if lags > AUTO_LAG_THRESHOLD:
        try:
            LOGGER.info(
                f"{lags} observations per day discovered. Using {lags} as maxlag setting for adfuller()"
            )
            (adfstat, pvalue, usedlag, nobs, critvalues) = adfuller(
                series, maxlag=lags, autolag=None
            )
            return AdfResultWrapper(
                adfstat, pvalue, usedlag, nobs, critvalues, icbest=None
            )
        except MissingDataError as e:
            logging.error(f"Error running adfuller test: {e}")
            raise ValueError(
                "Error running adfuller test, provided data contains missing values"
            ) from e
    else:
        # There are less than AUTO_LAG_THRESHOLD observations per day.
        # Let ADFuller determine the best 'maxlags' value to use.
        # The algo will give us the `icbest` value in return
        LOGGER.info(
            f"Less than {AUTO_LAG_THRESHOLD} observations per day discovered. We will let adfuller() decide "
            f"number of lags. (default 12*({len(df)}/100)^(1/4)) ~= {12 * (len(df) / 100) ** -.25}"
        )
        try:
            (adfstat, pvalue, usedlag, nobs, critvalues, icbest) = adfuller(series)
            return AdfResultWrapper(adfstat, pvalue, usedlag, nobs, critvalues, icbest)
        except MissingDataError as e:
            logging.error(f"Error running adfuller test: {e}")
            raise ValueError(
                "Error running adfuller test, provided data contains missing values"
            ) from e


def determine_lags_to_use(df: DataFrame, freq_override: str, lags: int):
    if lags:
        LOGGER.info(f"Lags value of {lags} provided. Skipping timestamp analysis.")
        return lags
    else:
        return obs_per_day(df, freq_override=freq_override)
