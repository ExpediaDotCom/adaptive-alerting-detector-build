from .seasonality_types import SeasonalityReport, SeasonalityResult


def annotate_seasonality(
    seasonality_result: SeasonalityResult,
    timeseries_name: str = "timeseries"
) -> SeasonalityReport:
    """
    Takes the given SeasonalityResult, generates some descriptive text fields and returns it as an
    SeasonalityReport.
    :param seasonality_result: StationarityResult
    :param timeseries_name: Text to show when generating description
    :return: StationarityReport
    """
    is_seasonal: bool = seasonality_result.is_seasonal
    period: int = seasonality_result.period
    # TODO: Add test details at the time the test is executed
    seasonality_display = _seasonality_details(is_seasonal)
    test_seasonal_display = _test_seasonal_details(period)
    return SeasonalityReport(
        timeseries_name + seasonality_display,
        is_seasonal,
        test_seasonal_display,
    )


def _seasonality_details(is_seasonal):
    return f"{' IS' if is_seasonal else ' is NOT'} seasonal"


def _test_seasonal_details(period: int):
    pass_test_seasonal_test = period is not None
    return (
        f"{'PASSED' if pass_test_seasonal_test else 'FAILED'}: "
        f"Calculated period is {period}, therefore metric is {'' if period else 'NOT'} seasonal'"
    )
