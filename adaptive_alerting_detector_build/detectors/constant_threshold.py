"""
Constant threshold detectors builders module.

This module provides functions to build constant threshold detectors that fit the provided metrics
data.
"""

import related
from typing import Optional
from enum import unique, Enum
import logging
import numpy as np
import pandas as pd
import numba

from numba import jit
# from adaptive_alerting_detector_build.detectors import exceptions
from . import Detector
from .exceptions import DetectorBuilderError

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@unique
class ConstantThresholdStrategy(Enum):
    """Constant threshold model fitting strategies"""

    SIGMA = "sigma"
    QUARTILE = "quartile"
    HIGHWATERMARK = "highwatermark"


@unique
class ConstantThresholdType(Enum):
    """Constant threshold model type"""

    RIGHT = "RIGHT_TAILED"
    LEFT = "LEFT_TAILED"
    TWO = "TWO_TAILED"


@related.mutable
class ConstantThresholdHyperparameters:
    strategy = related.ChildField(ConstantThresholdStrategy)
    lower_weak_multiplier = related.FloatField(default=4.0, required=False)
    lower_strong_multiplier = related.FloatField(default=5.0, required=False)
    upper_weak_multiplier = related.FloatField(default=4.0, required=False)
    upper_strong_multiplier = related.FloatField(default=5.0, required=False)
    hampel_window_size = related.FloatField(default=10, required=False)
    hampel_n_signma = related.FloatField(default=3, required=False)


@related.mutable
class ConstantThresholdThresholds:
    weak_upper_threshold = related.FloatField(key="upperWeak", required=False)
    strong_upper_threshold = related.FloatField(key="upperStrong", required=False)
    weak_lower_threshold = related.FloatField(key="lowerWeak", required=False)
    strong_lower_threshold = related.FloatField(key="lowerStrong", required=False)


@related.mutable
class ConstantThresholdParams:
    type = related.ChildField(ConstantThresholdType)
    thresholds = related.ChildField(ConstantThresholdThresholds)


@related.mutable
class ConstantThresholdTrainingMetaData:
    training_interval = related.StringField(default="7d", key="trainingInterval")


@related.mutable
class ConstantThresholdConfig:
    hyperparams = related.ChildField(ConstantThresholdHyperparameters)
    training_meta_data = related.ChildField(
        ConstantThresholdTrainingMetaData,
        key="trainingMetaData",
        default=ConstantThresholdTrainingMetaData(),
    )
    params = related.ChildField(ConstantThresholdParams, required=False)


class ConstantThresholdDetector(Detector):
    """Constant Threshold Detectors Builder class.

    This class provides methods to return a Detector object that fits provided metrics data, using
    one of the supported strategies.

    Currently supported strategies are:
        - sigma
        - quartile
    """

    id = "constant-detector"
    config_class = ConstantThresholdConfig
    # """

    # Calculations are performed on the provided data using the specified strategy, to determine
    # weak and strong thresholds.

    # Parameters:
    #     strategy: the strategy to use to determine thresholds; must be one from the Strategy
    #               class
    #     sample: list of number data on which calculations are performed
    #     weak_multiplier: number that represents to multiplier to use to calculate weak
    #                      thresholds
    #     strong_multiplier: number that represents to multiplier to use to calculate strong
    #                        thresholds

    # Returns:
    #     Detector object
    # """
    # return constant_threshold_config(**detector_config)

    def train(self, data, metric_type):
        """
        """
        data_drop_nan = data.dropna(axis=0, how="any", inplace=False)
        strategy = self.config.hyperparams.strategy

        threshold_type = _threshold_type(metric_type)
        if not threshold_type:
            raise DetectorBuilderError("Unknown metric_type")

        if strategy == ConstantThresholdStrategy.SIGMA:
            self._train_sigma(data_drop_nan, threshold_type)
        elif strategy == ConstantThresholdStrategy.QUARTILE:
            self._train_quartile(data_drop_nan, threshold_type)
        elif strategy == ConstantThresholdStrategy.HIGHWATERMARK:
            data_series = pd.Series(np.array(data.squeeze()))
            self._train_highwatermark(data_series, threshold_type)

    def _train_sigma(self, sample, threshold_type):
        """Performs threshold calculations using sigma (standard deviation) strategy.

        Parameters:
            sample: list of number data on which calculations are performed
            weak_multiplier: number that represents to multiplier to use to calculate weak
                            thresholds
            strong_multiplier: number that represents to multiplier to use to calculate strong
                            thresholds

        Returns:
            Detector object
        """

        sigma = _calculate_sigma(sample)
        mean = _calculate_mean(sample)
        weak_lower_threshold = mean - sigma * self.config.hyperparams.lower_weak_multiplier
        strong_lower_threshold = mean - sigma * self.config.hyperparams.lower_strong_multiplier
        weak_upper_threshold = mean + sigma * self.config.hyperparams.upper_weak_multiplier
        strong_upper_threshold = mean + sigma * self.config.hyperparams.upper_strong_multiplier

        self.config.params = ConstantThresholdParams(
            type=threshold_type,
            thresholds=ConstantThresholdThresholds(
                weak_upper_threshold=weak_upper_threshold,
                strong_upper_threshold=strong_upper_threshold,
                weak_lower_threshold=weak_lower_threshold,
                strong_lower_threshold=strong_lower_threshold,
            ),
        )

    def _train_quartile(self, sample, threshold_type):
        """Performs threshold calculations based on the interquartile range. 
            (https://en.wikipedia.org/wiki/Interquartile_range)
        Parameters:
            sample: list of number data on which calculations are performed

        Returns:
            Detector object
       """
        q1, median, q3 = _calculate_quartiles(sample)
        iqr = q3 - q1
        weak_lower_threshold = q1 - (q3 - q1) * self.config.hyperparams.lower_weak_multiplier
        strong_lower_threshold = q1 - (q3 - q1) * self.config.hyperparams.lower_strong_multiplier
        weak_upper_threshold = q3 + (q3 - q1) * self.config.hyperparams.upper_weak_multiplier
        strong_upper_threshold = q3 + (q3 - q1) * self.config.hyperparams.upper_strong_multiplier

        self.config.params = ConstantThresholdParams(
            type=threshold_type,
            thresholds=ConstantThresholdThresholds(
                weak_upper_threshold=weak_upper_threshold,
                strong_upper_threshold=strong_upper_threshold,
                weak_lower_threshold=weak_lower_threshold,
                strong_lower_threshold=strong_lower_threshold,
            ),
        )

    def _train_highwatermark(self, data, threshold_type):
        """Performs threshold calculations on the provided data using hampel filter and highwatermark.

        Parameters:
            data: list of number data on which calculations are performed
            metric_type: type of metric

        Returns:
            Detector object
        """

        clean_data = _data_cleanup(data)

        data_wo_outliers, outliers = _hampel_filter(np.array(clean_data, dtype=np.float64), 
                                                self.config.hyperparams.hampel_window_size, 
                                                self.config.hyperparams.hampel_n_signma)

        highwatermark = data_wo_outliers.max()

        strong_upper_threshold = self.config.hyperparams.upper_strong_multiplier * highwatermark
        weak_upper_threshold = self.config.hyperparams.upper_weak_multiplier * highwatermark
        
        self.config.params = ConstantThresholdParams(
            type=threshold_type,
            thresholds=ConstantThresholdThresholds(
                weak_upper_threshold=weak_upper_threshold,
                strong_upper_threshold=strong_upper_threshold,
            ),
        )


def _data_cleanup(input_series, trim_percentage=5):
    """Performs data cleanup:
            Trims data at the beginning and at the end by a given trim percentage.
            Removes NaN in the data.

        Parameters:
            input_series: input series of number data
            trim_percentage: percentage of data to be trimmed

        Returns:
            new_series: new series of data after cleanup
    """

    n = len(input_series)
    if n < 33:
        raise DetectorBuilderError("Sample must have at least thirty three elements")

    trim_beg = int((trim_percentage/100)*n)
    trim_end = int(((100-trim_percentage)/100)*n)

    new_series = input_series.drop(axis=0, labels=[i for i in range(0,trim_beg+1)], inplace=False)
    new_series = new_series.drop(axis=0, labels=[i for i in range(trim_end, n-1)], inplace=False)

    new_series = new_series.dropna(axis=0, how="any", inplace=False)

    return new_series


@jit(nopython=True)
def _hampel_filter(input_series, window_size=10, n_sigmas=3):
    """Performs outlier detection with Hampel Filter. The goal of the Hampel filter is to identify and replace outliers in a given series. 
        It uses a sliding window of configurable width to go over the data. For each window (given observation and the 2 window_size 
        surrounding elements, window_size for each side), we calculate the median and the standard deviation expressed as the median 
        absolute deviation(MAD).
        https://towardsdatascience.com/outlier-detection-with-hampel-filter-85ddf523c73d

        Parameters:
            input_series: input series of number data on which hampel filter is applied
            window_size: the size of the sliding window
            n_sigmas: the number of standard deviations which identify the outlier

        Returns:
            series_wo_outliers: series of data with outliers removed and replaced with MAD
            outliers: list of detected outliers
    """
    
    n = len(input_series)
    if n < 30:
        raise DetectorBuilderError("Sample must have at least thirty elements")
    
    series_wo_outliers = input_series.copy()
    k = 1.4826 # scale factor for Gaussian distribution
    outliers = []
    
    for i in range((window_size),(n - window_size)):
        x0 = np.nanmedian(input_series[(i - window_size):(i + window_size)])
        S0 = k * np.nanmedian(np.abs(input_series[(i - window_size):(i + window_size)] - x0))
        if (np.abs(input_series[i] - x0) > n_sigmas * S0):
            series_wo_outliers[i] = x0
            outliers.append(i)
    
    return series_wo_outliers, outliers


def _threshold_type(metric_type):
    mappings = {
        "REQUEST_COUNT": ConstantThresholdType.TWO,
        "ERROR_COUNT": ConstantThresholdType.RIGHT,
        "SUCCESS_RATE": ConstantThresholdType.LEFT,
        "LATENCY": ConstantThresholdType.RIGHT,
    }
    return mappings.get(metric_type, None)


def _calculate_sigma(sample):
    """Calculates and returns the sigma (standard deviation) of the provided sample.

    Parameters:
        sample: list of number data on which calculations are performed
    """
    if len(sample) < 2:
        raise DetectorBuilderError("Sample must have at least two elements")
    array = np.array(sample)
    return np.std(array, ddof=1)


def _calculate_mean(sample):
    """Calculates and returns the mean of the provided sample.

    Parameters:
        sample: list of number data on which calculations are performed
    """

    array = np.array(sample)
    return np.mean(array)


def _calculate_quartiles(sample):
    """Calculates and returns quartiles for the provided sample.

    Note that "quartiles" are calculated using 25th, 50th, and 75th percentile, and may differ than
    quartiles calculated manually.

    Parameters:
        sample: list of number data on which calculations are performed

    Returns:
        a list containing the first quartile, median and third quartile values
    """

    array = np.array(sample)
    return np.percentile(array, [25, 50, 75], interpolation="midpoint")
