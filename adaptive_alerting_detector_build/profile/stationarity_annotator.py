from .stationarity_checker import DEFAULT_MAX_ADF_PVALUE, DEFAULT_SIGNIFICANCE
from .stationarity_types import StationarityResult, StationarityReport, AdfResultWrapper


def annotate_stationarity(
    stationarity_result: StationarityResult,
    timeseries_name: str = "timeseries",
    significance: str = DEFAULT_SIGNIFICANCE,
    max_adf_pvalue=DEFAULT_MAX_ADF_PVALUE,
) -> StationarityReport:
    """
    Takes the given StationarityResult, generates some descriptive text fields and returns it as an
    StationarityReport.
    :param stationarity_result: StationarityResult
    :param timeseries_name: Text to show when generating description
    :param max_adf_pvalue: Augmented Dicker-Fuller test result must be less than or equal to this number
    :return: StationarityReport
    """
    is_stationary: bool = stationarity_result.is_stationary
    adf_result: AdfResultWrapper = stationarity_result.adf_result
    # TODO: Add test details at the time the test is executed
    stationarity_display = _stationarity_details(is_stationary)
    test_stat_display = _test_stat_details(adf_result, significance)
    p_value_display = _p_value_details(adf_result.pvalue, max_adf_pvalue)
    adf_summary = f"{timeseries_name} {stationarity_display}\n{test_stat_display}\n{p_value_display}"
    return StationarityReport(
        adf_result,
        adf_summary,
        p_value_display,
        stationarity_display,
        is_stationary,
        test_stat_display,
    )


def _stationarity_details(is_stationary):
    result = f"{'IS' if is_stationary else 'is NOT'} stationary "
    result += f"(we {'can' if is_stationary else 'cannot'} reject the Null Hypothesis that there is a unit root)\n"
    result += f"{'At least one of' if is_stationary else 'None of'} these Stationarity tests PASSED:"
    return result


def _test_stat_details(adf_result_wrapper: AdfResultWrapper, significance: str):
    significance_value = adf_result_wrapper.critvalues[significance]
    pass_test_stat_test = adf_result_wrapper.adfstat < significance_value
    return (
        f"{'PASSED' if pass_test_stat_test else 'FAILED'}: "
        f"Test statistic ({adf_result_wrapper.adfstat:.5f}) {'<' if pass_test_stat_test else 'is not less than'} "
        f"{significance} confidence interval ({significance_value:.3f})"
    )


def _p_value_details(p_value: float, max_adf_pvalue: float):
    pass_p_value_test = p_value < max_adf_pvalue
    return (
        f"{'PASSED' if pass_p_value_test else 'FAILED'}: "
        f"p-value ({p_value:.5f}) {'<' if pass_p_value_test else 'is not less than'} {max_adf_pvalue:.5f} "
        f"({'' if pass_p_value_test else 'NOT '}statistically significant)"
    )
