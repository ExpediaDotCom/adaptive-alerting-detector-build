from adaptivealerting.metric_profiler.stationarity import is_stationary


def build_profile(x):
    """
    Builds a feature profile of the given time series.

    :param x: time series
    :return: time series feature profile
    """

    return {
        "stationary": is_stationary(x, "1%")
    }
