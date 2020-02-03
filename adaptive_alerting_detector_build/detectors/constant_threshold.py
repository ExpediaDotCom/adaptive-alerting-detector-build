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

# from adaptive_alerting_detector_build.detectors import exceptions
from . import DetectorBase
from .exceptions import DetectorBuilderError
from adaptive_alerting_detector_build.utils.attrs import validate


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@unique
class ConstantThresholdStrategy(Enum):
    """Constant threshold model fitting strategies"""
    SIGMA = "sigma"
    QUARTILE = "quartile"

@unique
class ConstantThresholdType(Enum):
    """Constant threshold model type"""
    RIGHT = "RIGHT_TAILED" 
    LEFT = "LEFT_TAILED" 
    TWO = "TWO_TAILED"


@related.mutable
class ConstantThresholdHyperparameters:
    strategy = related.ChildField(ConstantThresholdStrategy)
    weak_multiplier = related.FloatField(default=1.0)
    strong_multiplier = related.FloatField(default=1.0)

@related.mutable
class ConstantThresholdThresholds:
    weak_upper_threshold = related.FloatField(key='upperWeak') 
    strong_upper_threshold = related.FloatField(key='upperStrong')
    weak_lower_threshold = related.FloatField(key='lowerWeak')
    strong_lower_threshold = related.FloatField(key='lowerStrong')


@related.mutable
class ConstantThresholdParams:
    type = related.ChildField(ConstantThresholdType)
    thresholds = related.ChildField(ConstantThresholdThresholds)

@related.mutable
class ConstantThresholdConfig:
    hyperparameters = related.ChildField(ConstantThresholdHyperparameters)
    params = related.ChildField(ConstantThresholdParams, required=False)


class ConstantThresholdDetector(DetectorBase):
    """Constant Threshold Detectors Builder class.

    This class provides methods to return a Detector object that fits provided metrics data, using
    one of the supported strategies.

    Currently supported strategies are:
        - sigma
        - quartile
    """
    # config = attr.ib(validator=attr.validators.instance_of(ConstantThresholdConfig))
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


    def train(self, data):
        """
        """
        strategy = self.config.hyperparameters.strategy
        if strategy == ConstantThresholdStrategy.SIGMA:
            self._train_sigma(data)
        elif strategy == ConstantThresholdStrategy.QUARTILE:
            self._train_quartile(data)

    def _train_sigma(self, sample):
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
        weak_upper_threshold, weak_lower_threshold = _calculate_sigma_thresholds(
            sigma, mean, self.config.hyperparameters.weak_multiplier
        )
        strong_upper_threshold, strong_lower_threshold = _calculate_sigma_thresholds(
            sigma, mean, self.config.hyperparameters.strong_multiplier
        )

        self.config.params = ConstantThresholdParams(
            type = ConstantThresholdType.TWO, #TODO: Default to TWO for now. To be determined by Profiler.
            thresholds = ConstantThresholdThresholds(
                            weak_upper_threshold=weak_upper_threshold,
                            strong_upper_threshold=strong_upper_threshold,
                            weak_lower_threshold=weak_lower_threshold,
                            strong_lower_threshold=strong_lower_threshold
            )
        )
        

    def _train_quartile(self, sample):
        """Performs threshold calculations using quartile strategy.

        Parameters:
            sample: list of number data on which calculations are performed
            weak_multiplier: number that represents to multiplier to use to calculate weak
                             thresholds
            strong_multiplier: number that represents to multiplier to use to calculate strong
                               thresholds

        Returns:
            Detector object
       """
        q1, median, q3 = _calculate_quartiles(sample)
        weak_upper_threshold, weak_lower_threshold = _calculate_quartile_thresholds(
            q1, q3, self.config.hyperparameters.weak_multiplier
        )
        strong_upper_threshold, strong_lower_threshold = _calculate_quartile_thresholds(
            q1, q3, self.config.hyperparameters.strong_multiplier
        )

        self.config.params = ConstantThresholdParams(
            type = ConstantThresholdType.TWO, 
            thresholds = ConstantThresholdThresholds(
                            weak_upper_threshold=weak_upper_threshold,
                            strong_upper_threshold=strong_upper_threshold,
                            weak_lower_threshold=weak_lower_threshold,
                            strong_lower_threshold=strong_lower_threshold
            )
        )
        




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


def _calculate_sigma_thresholds(sigma, mean, multiplier):
    """Calculates and returns the thresholds using sigmas.

    Parameters:
        sigma: standard deviation value
        mean: mean of the provided sample
        multiplier: number by which to multiply the sigma to add/subtract from the mean

    Returns:
        a list containing the upper and lower threshold values
    """

    upper = mean + sigma * multiplier
    lower = mean - sigma * multiplier
    return upper, lower


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


def _calculate_quartile_thresholds(q1, q3, multiplier):
    """Calculates and returns the thresholds using quartiles.

    Parameters:
        q1: first quartile value
        q3: third quartile value
        multiplier: number by which to multiply the inter-quartile-range to add/subtract from the
                    quartiles

    Returns:
        a list containing the upper and lower threshold values
    """

    iqr = q3 - q1
    upper = q3 + iqr * multiplier
    lower = q1 - iqr * multiplier
    return upper, lower
