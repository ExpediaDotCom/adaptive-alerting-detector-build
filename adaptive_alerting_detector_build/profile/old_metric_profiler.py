import logging

from .stationarity_annotator import annotate_stationarity
from .stationarity_display import print_stationarity_report
from .stationarity_types import AdfResultWrapper, StationarityResult, StationarityReport

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def old_build_profile(df):
    """
    Builds a feature profile of the given time series.

    :param x: time series
    :return: time series feature profile
    """

    def pprints(result: AdfResultWrapper):
        import pandas as pd

        dfoutput = pd.Series(
            [result.adfstat, result.pvalue, result.usedlag, result.nobs],
            index=[
                "Test Statistic",
                "p-value",
                "#Lags Used",
                "Number of Observations Used",
            ],
        )
        for key, value in result.critvalues.items():
            dfoutput["Critical Value (%s)" % key] = value
        from .df_helper import convert_df_to_str

        return convert_df_to_str(dfoutput)

    def _is_stationary(x, significance):
        """
        Runs a stationarity test on the time series.

        :param x: time series
        :param significance: valid values are "1%", "5%" and "10%"
        :return: boolean indicating whether the time series is stationary, assuming the given significance level
        """
        from statsmodels.tsa.stattools import adfuller

        result = adfuller(x)
        (adfstat, pvalue, usedlag, nobs, critvalues, icbest) = result
        adf_result_wrapper = AdfResultWrapper(
            adfstat, pvalue, usedlag, nobs, critvalues, icbest
        )
        significance_value = adf_result_wrapper.critvalues[significance]
        is_stationary = bool(adf_result_wrapper.adfstat < significance_value)
        stationarity_result = StationarityResult(
            is_stationary=is_stationary, adf_result=adf_result_wrapper
        )

        LOGGER.info(
            f"\ncritvalue[{significance}]={result[4][significance]}, test_stat={result[0]}, p_value={result[1]}"
        )

        stationarity_report: StationarityReport = annotate_stationarity(
            stationarity_result, max_adf_pvalue=0.05
        )
        print_stationarity_report(stationarity_report)

        return result[0] < result[4][significance]

    from .df_helper import df_values_as_array

    x = df_values_as_array(df)
    return {"stationary": _is_stationary(x, "1%")}
