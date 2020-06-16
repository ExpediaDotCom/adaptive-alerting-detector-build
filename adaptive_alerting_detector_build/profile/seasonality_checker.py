import logging

import numpy as np
from pandas import DataFrame
from seasonal import fit_seasons

from .seasonality_types import SeasonalityResult

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# minimum of two seasons is recommended, ideally 3
MINIMUM_NUMBER_OF_SEASONS = 3


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
    :param period: optional seasonality period
    :return: SeasonalityResult
    """

    data = _preprocess_data(df)

    if data.size == 0:
        raise ValueError("Data for seasonality test is not valid. Check if length of your dataset is 0.")

    number_of_datapoints = data.size
    if period and number_of_datapoints < period * MINIMUM_NUMBER_OF_SEASONS:
        raise ValueError(f"Number of datapoints is less than minimum recommended number of datapoints. Make sure that the number of"
                         f"datapoints is at least {period} * {MINIMUM_NUMBER_OF_SEASONS} (period * MINIMUM_NUMBER_OF_SEASONS)")

    LOGGER.info('Running seasonality test...')
    seasons, trend = fit_seasons(data, period=period)

    if seasons is not None:
        period = len(seasons)
    else:
        period = None
    is_seasonal = period is not None
    return SeasonalityResult(is_seasonal=is_seasonal, period=period)
