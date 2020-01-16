"""
Constant threshold detectors builders module.

This module provides functions to build constant threshold detectors that fit the provided metrics
data.
"""

from enum import Enum
import logging
import numpy as np
from adaptive_alerting_detector_build.detectors import base_detector
from adaptive_alerting_detector_build.detectors import exceptions
import attr

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class constant_threshold_strategy(Enum):
    """Constant threshold model fitting strategies"""

    SIGMA = "sigma"
    QUARTILE = "quartile"

@attr.s
class constant_threshold_training_metadata:
    strategy = attr.ib(default = constant_threshold_strategy.SIGMA,
        validator=attr.validators.in_(constant_threshold_strategy),
        converter=constant_threshold_strategy)
    weak_multiplier = attr.ib(default=1)
    strong_multiplier = attr.ib(default=1)

@attr.s
class constant_threshold_hyperparametrs:
    weak_upper_threshold = attr.ib()
    strong_upper_threshold = attr.ib()
    weak_lower_threshold = attr.ib()
    strong_lower_threshold = attr.ib()

@attr.s
class constant_threshold_config:
    training_metadata = attr.ib(validator=attr.validators.instance_of(constant_threshold_training_metadata))
    hyperparameters = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(constant_threshold_hyperparametrs)))


class constant_threshold(base_detector):
    """Constant Threshold Detectors Builder class.

    This class provides methods to return a Detector object that fits provided metrics data, using
    one of the supported strategies.

    Currently supported strategies are:
        - sigma
        - quartile
    """

    def builder(self, config):
        """Performs calculations and returns a detector object.

        Calculations are performed on the provided data using the specified strategy, to determine
        weak and strong thresholds.

        Parameters:
            strategy: the strategy to use to determine thresholds; must be one from the Strategy
                      class
            sample: list of number data on which calculations are performed
            weak_multiplier: number that represents to multiplier to use to calculate weak
                             thresholds
            strong_multiplier: number that represents to multiplier to use to calculate strong
                               thresholds

        Returns:
            Detector object
        """
        return constant_threshold_config(
            training_metadata = constant_threshold_training_metadata(**config),
            hyperparameters = None
        )

    def train(self, data):
        strategy = self.config.training_metadata.strategy
        if strategy == constant_threshold_strategy.SIGMA:
            self._train_sigma(data)
        elif strategy == constant_threshold_strategy.QUARTILE:
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
            sigma, mean, self.config.training_metadata.weak_multiplier)
        strong_upper_threshold, strong_lower_threshold = _calculate_sigma_thresholds(
            sigma, mean, self.config.training_metadata.strong_multiplier)

        
        hyperparameters = constant_threshold_hyperparametrs(
            weak_upper_threshold,
            strong_upper_threshold,
            weak_lower_threshold,
            strong_lower_threshold
        )
        # print('hyperparameters',hyperparameters)
        self.config.hyperparameters = hyperparameters

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
        weak_upper_threshold, weak_lower_threshold = \
                _calculate_quartile_thresholds(q1, q3, self.config.training_metadata.weak_multiplier)
        strong_upper_threshold, strong_lower_threshold = \
                _calculate_quartile_thresholds(q1, q3, self.config.training_metadata.strong_multiplier)

        hyperparameters = constant_threshold_hyperparametrs(
            weak_upper_threshold,
            strong_upper_threshold,
            weak_lower_threshold,
            strong_lower_threshold
        )
        # print('hyperparameters',hyperparameters)
        self.config.hyperparameters = hyperparameters


def _calculate_sigma(sample):
    """Calculates and returns the sigma (standard deviation) of the provided sample.

    Parameters:
        sample: list of number data on which calculations are performed
    """
    if len(sample) < 2:
        raise exceptions.DetectorBuilderError("Sample must have at least two elements")
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
    return np.percentile(array, [25, 50, 75], interpolation='midpoint')

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
