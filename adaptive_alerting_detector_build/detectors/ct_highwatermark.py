"""
Constant threshold highwatermark detectors builders module.

This module provides functions to build constant threshold detectors that fit the provided metrics
data.
"""

import related
from enum import unique, Enum
import logging
import numpy as np
import pandas as pd
import numba

from numba import jit
from . import Detector

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

@unique
class CTHighwatermarkType(Enum):
    """Constant threshold highwatermark model type"""

    RIGHT = "RIGHT_TAILED"
    LEFT = "LEFT_TAILED"
    TWO = "TWO_TAILED"


@related.mutable
class CTHighwatermarkHyperparameters:
    upper_weak_multiplier = related.FloatField(default=1.10, required=False)
    upper_strong_multiplier = related.FloatField(default=1.05, required=False)
    hampel_window_size = related.FloatField(default=10, required=False)
    hampel_n_signma = related.FloatField(default=3, required=False)


@related.mutable
class CTHighwatermarkThresholds:
    upper_weak_threshold = related.FloatField(key="upperWeak", required=False)
    upper_strong_threshold = related.FloatField(key="upperStrong", required=False)


@related.mutable
class CTHighwatermarkParams:
    type = related.ChildField(CTHighwatermarkType)
    thresholds = related.ChildField(CTHighwatermarkThresholds)


@related.mutable
class CTHighwatermarkTrainingMetaData:
    training_interval = related.StringField(default="7d", key="trainingInterval")


@related.mutable
class CTHighwatermarkDetectorMetaData:
    subtype = related.StringField(default="ct-highwatermark-detector", required=False)

@related.mutable
class CTHighwatermarkConfig:
    hyperparams = related.ChildField(CTHighwatermarkHyperparameters)
    training_meta_data = related.ChildField(
        CTHighwatermarkTrainingMetaData,
        key="trainingMetaData",
        default=CTHighwatermarkTrainingMetaData(),
    )
    params = related.ChildField(CTHighwatermarkParams, required=False)
    detector_meta_data = related.ChildField(
        CTHighwatermarkDetectorMetaData, 
        key="detectorMetaData",
        required=False)


class CTHighwatermarkDetector(Detector):
    """Constant Threshold Highwatermark Detectors Builder class.

    This class provides methods to return a Detector object that fits provided metrics data.

    """

    id = "ct-highwatermark-detector"
    config_class = CTHighwatermarkConfig
    """

    Calculations are performed on the provided data using hampel filter and highwatermark,
    to determine weak and strong thresholds.

    Parameters:
        data: list of number data on which calculations are performed
        metric_type: type of metric
        weak_multiplier: number that represents the multiplier to use to calculate weak
                         thresholds
        strong_multiplier: number that represents the multiplier to use to calculate strong
                           thresholds
        hampel_window_size: the size of the sliding window
        hampel_n_sigma: the number of standard deviations which identify the outlier
    Returns:
        Detector object
    """

    def train(self, data, metric_type):
        """Performs threshold calculations on the provided data using hampel filter and highwatermark.

        Parameters:
            data: list of number data on which calculations are performed
            metric_type: type of metric

        Returns:
            Detector object
        """
        threshold_type = _threshold_type(metric_type)

        data_drop_nan = data.dropna(axis=0, how="any", inplace=False)

        data_wo_outliers, outliers = _hampel_filter(np.array(data_drop_nan, dtype=np.float64), 
                                                self.config.hyperparams.hampel_window_size, 
                                                self.config.hyperparams.hampel_n_signma)

        highwatermark = data_wo_outliers.max()

        upper_strong_threshold = self.config.hyperparams.upper_strong_multiplier * highwatermark
        upper_weak_threshold = self.config.hyperparams.upper_weak_multiplier * highwatermark
        
        self.config.params = CTHighwatermarkParams(
            type=threshold_type,
            thresholds=CTHighwatermarkThresholds(
                upper_weak_threshold=upper_weak_threshold,
                upper_strong_threshold=upper_strong_threshold,
            ),
        )
   

def _threshold_type(metric_type):
    mappings = {
        "REQUEST_COUNT": CTHighwatermarkType.TWO,
        "ERROR_COUNT": CTHighwatermarkType.RIGHT,
        "SUCCESS_RATE": CTHighwatermarkType.LEFT,
        "LATENCY_AVG": CTHighwatermarkType.RIGHT,
    }
    return mappings.get(metric_type, None)


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