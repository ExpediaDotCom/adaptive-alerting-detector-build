import logging

from pandas import DataFrame
from statsmodels.tools.sm_exceptions import MissingDataError
from statsmodels.tsa.stattools import adfuller

from .df_helper import df_values_as_array
from .df_helper import obs_per_day
from .stationarity_types import AdfResultWrapper, StationarityResult

DEFAULT_SIGNIFICANCE = "1%"
DEFAULT_MAX_ADF_PVALUE = 0.05

# There must be at least this number of observations in one day to use our calculated lags,
#   otherwise stattools.adfuller() will derive its own default
# TODO: Make this configurable
AUTO_LAG_THRESHOLD = 24

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def stationarity_check(df: DataFrame,
                       freq: str = None,
                       max_adf_pvalue: float = DEFAULT_MAX_ADF_PVALUE,
                       significance: str = DEFAULT_SIGNIFICANCE,
                       lags: int = None) -> StationarityResult:
    """
    Performs a stationarity check using stattools.adfuller().
    Wraps the resulting array in a stronger AdfResultWrapper type.
    Performs a test using the given max_adf_pvalue and significance.  Results
    :param df: Pandas DataFrame with DateTimeIndex
    :param freq: Frequency string such as '1D' for 1 day, '5T' for 5 minutes, etc.
                 See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    :param max_adf_pvalue: Augmented Dicker-Fuller test result must be less than or equal to this number
    :param significance: Which significance value should be used for test? Valid values are "1%", "5%" and "10%"
    :param lags: The number of lags that should be checked for unit root. If None, defaults to number of observations
                 per day (which is derived from the frequency observed in timestamps in provided df)
    :return: StationarityResult
    """
    adf_result: AdfResultWrapper = _adf_stationarity_test(df=df, freq_override=freq, lags=lags)
    significance_value = adf_result.critvalues[significance]
    passes_significance_test = adf_result.adfstat < significance_value
    # Should we use p-value at all?
    # From the adfuller docs:  "If the p-value is close to significant, then the critical values should be used to
    #                           judge whether to reject the null."
    passes_pvalue_test = adf_result.pvalue <= max_adf_pvalue
    is_stationary = bool(passes_significance_test or passes_pvalue_test)
    return StationarityResult(is_stationary=is_stationary, adf_result=adf_result)


def _adf_stationarity_test(df: DataFrame, freq_override: str = None, lags: int = None) -> AdfResultWrapper:
    """

    :param df: Pandas DataFrame with DateTimeIndex
    :param freq_override: Explicit frequency to use in cases where provided df does not have a DateTimeIndex index
    :param lags: The number of lags that should be checked for unit root. If None, defaults to number of observations
                 per day (which is derived from the frequency observed in timestamps in provided df)
    :return: AdfResultWrapper with icbest = None when lags (provided or auto-derived) > AUTO_LAG_THRESHOLD
    """
    series = df_values_as_array(df)
    lags = determine_lags_to_use(df, freq_override, lags)
    if lags > AUTO_LAG_THRESHOLD:
        try:
            LOGGER.info(f"{lags} observations per day discovered. Using {lags} as maxlag setting for adfuller()")
            (adfstat, pvalue, usedlag, nobs, critvalues) = adfuller(series, maxlag=lags, autolag=None)
            return AdfResultWrapper(adfstat, pvalue, usedlag, nobs, critvalues, icbest=None)
        except MissingDataError as e:
            logging.error(f"Error running adfuller test: {e}")
            raise ValueError("Error running adfuller test, provided data contains missing values") from e
    else:
        # There are less than AUTO_LAG_THRESHOLD observations per day.
        # Let ADFuller determine the best 'maxlags' value to use.
        # The algo will give us the `icbest` value in return
        LOGGER.info(f"Less than {AUTO_LAG_THRESHOLD} observations per day discovered. We will let adfuller() decide "
                     f"number of lags. (default 12*({len(df)}/100)^(1/4)) ~= {12 * (len(df) / 100) ** -.25}")
        try:
            (adfstat, pvalue, usedlag, nobs, critvalues, icbest) = adfuller(series)
            return AdfResultWrapper(adfstat, pvalue, usedlag, nobs, critvalues, icbest)
        except MissingDataError as e:
            logging.error(f"Error running adfuller test: {e}")
            raise ValueError("Error running adfuller test, provided data contains missing values") from e


def determine_lags_to_use(df: DataFrame, freq_override: str, lags: int):
    if lags:
        LOGGER.info(f"Lags value of {lags} provided. Skipping timestamp analysis.")
        return lags
    else:
        return obs_per_day(df, freq_override=freq_override)
