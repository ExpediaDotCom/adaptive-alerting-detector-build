"""
Detectors builders module.

This module provides functions to build detectors that fit the provided metrics data.
"""

from enum import Enum
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class DetectorBuilderError(Exception):
    """Base class for detector builder errors."""
    pass

class Detector:
    """Detector that is used by Adaptive Alerting to find anomalies.

    Detector model contains thresholds for weak and strong anomalies.

    Arguments:

    """
    def __init__(self, build_strategy, weak_multiplier, strong_multiplier,
                 weak_upper_threshold, strong_upper_threshold, weak_lower_threshold,
                 strong_lower_threshold):
    # TODO: Convert to **kwargs
        self.build_strategy = build_strategy
        self.weak_multiplier = weak_multiplier
        self.strong_multiplier = strong_multiplier
        self.weak_upper_threshold = weak_upper_threshold
        self.strong_upper_threshold = strong_upper_threshold
        self.weak_lower_threshold = weak_lower_threshold
        self.strong_lower_threshold = strong_lower_threshold


class DetectorBuilder:
    """Base class for detectors builders."""
    pass

class ConstantThresholdDetectorBuilder(DetectorBuilder):
    """Constant Threshold Detectors Builder class.

    This class provides methods to return a Detector object that fits provided metrics data, using
    one of the supported strategies.

    Currently supported strategies are:
        - sigma
        - quartile
    """

    class Strategy(Enum):
        """Constant threshold model fitting strategies"""

        SIGMA = "sigma"
        QUARTILE = "quartile"

    def detector(self, strategy, sample, weak_multiplier, strong_multiplier):
        """Performs calculations and returns a detector object.

        Calculations are performed on the provided data using the specified strategy, to determine
        weak and strong thresholds.

        Arguments:
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

        if strategy == self.Strategy.SIGMA:
            return self._create_sigma_detector(sample, weak_multiplier, strong_multiplier)
        if strategy == self.Strategy.QUARTILE:
            return self._create_quartile_detector(sample, weak_multiplier, strong_multiplier)
        raise DetectorBuilderError("Unknown build strategy")

    def _create_sigma_detector(self, sample, weak_multiplier, strong_multiplier):
        """Performs threshold calculations using sigma (standard deviation) strategy.

        Arguments:
            sample: list of number data on which calculations are performed
            weak_multiplier: number that represents to multiplier to use to calculate weak
                             thresholds
            strong_multiplier: number that represents to multiplier to use to calculate strong
                               thresholds

        Returns:
            Detector object
       """

        STRATEGY = self.Strategy.SIGMA

        sigma = calculate_sigma(sample)
        mean = calculate_mean(sample)
        weak_upper_threshold, weak_lower_threshold = calculate_sigma_thresholds(
            sigma, mean, weak_multiplier)
        strong_upper_threshold, strong_lower_threshold = calculate_sigma_thresholds(
            sigma, mean, strong_multiplier)

        return Detector(STRATEGY, weak_multiplier, strong_multiplier,
                        weak_upper_threshold, strong_upper_threshold,
                        weak_lower_threshold, strong_lower_threshold)

    def _create_quartile_detector(self, sample, weak_multiplier, strong_multiplier):
        """Performs threshold calculations using quartile strategy.

        Arguments:
            sample: list of number data on which calculations are performed
            weak_multiplier: number that represents to multiplier to use to calculate weak
                             thresholds
            strong_multiplier: number that represents to multiplier to use to calculate strong
                               thresholds

        Returns:
            Detector object
       """

        STRATEGY = self.Strategy.QUARTILE

        q1, median, q3 = calculate_quartiles(sample)
        weak_upper_threshold, weak_lower_threshold = \
                calculate_quartile_thresholds(q1, q3, weak_multiplier)
        strong_upper_threshold, strong_lower_threshold = \
                calculate_quartile_thresholds(q1, q3, strong_multiplier)

        return Detector(STRATEGY, weak_multiplier, strong_multiplier,
                        weak_upper_threshold, strong_upper_threshold,
                        weak_lower_threshold, strong_lower_threshold)


def calculate_sigma(sample):
    """Calculates and returns the sigma (standard deviation) of the provided sample.

    Arguments:
        sample: list of number data on which calculations are performed
    """

    if len(sample) < 2:
        raise Exception("Sample must have at least two elements")
    array = np.array(sample)
    return np.std(array, ddof=1)

def calculate_mean(sample):
    """Calculates and returns the mean of the provided sample.

    Arguments:
        sample: list of number data on which calculations are performed
    """

    array = np.array(sample)
    return np.mean(array)

def calculate_sigma_thresholds(sigma, mean, multiplier):
    """Calculates and returns the thresholds using sigmas.

    Arguments:
        sigma: standard deviation value
        mean: mean of the provided sample
        multiplier: number by which to multiply the sigma to add/subtract from the mean

    Returns:
        a list containing the upper and lower threshold values
    """

    upper = mean + sigma * multiplier
    lower = mean - sigma * multiplier
    return upper, lower

def calculate_quartiles(sample):
    """Calculates and returns quartiles for the provided sample.

    Note that "quartiles" are calculated using 25th, 50th, and 75th percentile, and may differ than
    quartiles calculated manually.

    Arguments:
        sample: list of number data on which calculations are performed

    Returns:
        a list containing the first quartile, median and third quartile values
    """

    array = np.array(sample)
    return np.percentile(array, [25, 50, 75], interpolation='midpoint')

def calculate_quartile_thresholds(q1, q3, multiplier):
    """Calculates and returns the thresholds using quartiles.

    Arguments:
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


# TODO: Add logging
