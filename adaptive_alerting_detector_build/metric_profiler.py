from statsmodels.tsa.stattools import adfuller


def build_profile(x):
    """
    Builds a feature profile of the given time series.

    :param x: time series
    :return: time series feature profile
    """

    return {"stationary": _is_stationary(x, "1%")}


def _is_stationary(x, significance):
    """
    Runs a stationarity test on the time series.

    :param x: time series
    :param significance: valid values are "1%", "5%" and "10%"
    :return: boolean indicating whether the time series is stationary, assuming the given significance level
    """
    result = adfuller(x)
    test_stat = result[0]
    p_value = result[1]
    crit_value = result[4][significance]
    print(
        "\ncrit_value_{}={}, test_stat={}, p_value={}".format(
            crit_value, test_stat, significance, p_value
        )
    )
    return test_stat < crit_value
