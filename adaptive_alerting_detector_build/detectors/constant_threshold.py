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
from . import Detector
from .exceptions import DetectorBuilderError

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
    lower_weak_multiplier = related.FloatField(default=4.0, required=False)
    lower_strong_multiplier = related.FloatField(default=5.0, required=False)
    upper_weak_multiplier = related.FloatField(default=4.0, required=False)
    upper_strong_multiplier = related.FloatField(default=5.0, required=False)


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
        default=ConstantThresholdTrainingMetaData()
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

    def train(self, data):
        """
        """
        data_drop_nan = data.dropna(axis=0, how="any", inplace=False)
        strategy = self.config.hyperparams.strategy
        if strategy == ConstantThresholdStrategy.SIGMA:
            self._train_sigma(data_drop_nan)
        elif strategy == ConstantThresholdStrategy.QUARTILE:
            self._train_quartile(data_drop_nan)

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
        weak_lower_threshold = mean - sigma * self.config.hyperparams.lower_weak_multiplier
        strong_lower_threshold = mean - sigma * self.config.hyperparams.lower_strong_multiplier
        weak_upper_threshold = mean + sigma * self.config.hyperparams.upper_weak_multiplier
        strong_upper_threshold = mean + sigma * self.config.hyperparams.upper_strong_multiplier

        self.config.params = ConstantThresholdParams(
            type=ConstantThresholdType.TWO,  # TODO: Default to TWO for now. To be determined by Profiler.
            thresholds=ConstantThresholdThresholds(
                weak_upper_threshold=weak_upper_threshold,
                strong_upper_threshold=strong_upper_threshold,
                weak_lower_threshold=weak_lower_threshold,
                strong_lower_threshold=strong_lower_threshold,
            ),
        )

    def _train_quartile(self, sample):
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
            type=ConstantThresholdType.TWO,
            thresholds=ConstantThresholdThresholds(
                weak_upper_threshold=weak_upper_threshold,
                strong_upper_threshold=strong_upper_threshold,
                weak_lower_threshold=weak_lower_threshold,
                strong_lower_threshold=strong_lower_threshold,
            ),
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




