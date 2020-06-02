import logging

from pandas import DataFrame

from .seasonality_annotator import annotate_seasonality
from .seasonality_checker import (
    seasonality_check
)
from .seasonality_display import print_seasonality_report
from .seasonality_types import SeasonalityResult, SeasonalityReport

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def build_seasonal_profile(
    df: DataFrame,
    period: int = None
):
    """
    Builds a seasonality profile of the given time series.

    :param df: Pandas DataFrame with DateTimeIndex
    :param period: Optional period to provide to seasonal test. It is advised to provide a period with the timeseries if
                    it is known, to reduce algorithm complexity and increase accuracy.
    :return: the result of seasonality test
    """
    seasonality_result: bool = _is_seasonal(
        df=df,
        period=period
    )
    return {"seasonal": seasonality_result}


def _is_seasonal(
    df: DataFrame,
    period: int = None
) -> bool:
    """
    Runs a seasonality test on a time series.

    :param df: Pandas DataFrame with DateTimeIndex
    :param period: Optional period to provide to seasonal test. It is advised to provide a period with the timeseries if
                   it is known, to reduce algorithm complexity and increase accuracy.
    :return: boolean indicating whether the time series is seasonal
    """
    seasonality_result: SeasonalityResult = _try_seasonality_check(
        df=df,
        period=period
    )
    seasonality_report: SeasonalityReport = annotate_seasonality(seasonality_result)
    print_seasonality_report(seasonality_report)
    return seasonality_result.is_seasonal


def _try_seasonality_check(
    df: DataFrame,
    period: int = None
) -> SeasonalityResult:
    try:
        return seasonality_check(
            df=df,
            period=period
        )
    except Exception as e:
        raise ValueError("Encountered error during seasonal test") from e
