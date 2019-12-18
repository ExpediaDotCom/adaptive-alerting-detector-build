from enum import Enum
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class Detector:
    def __init__(self, training_strategy, weak_multiplier, strong_multiplier,
                 weak_upper_threshold, strong_upper_threshold, weak_lower_threshold,
                 strong_lower_threshold):
    # TODO: Convert to **kwargs
        self.training_strategy = training_strategy
        self.weak_multiplier = weak_multiplier
        self.strong_multiplier = strong_multiplier
        self.weak_upper_threshold = weak_upper_threshold
        self.strong_upper_threshold = strong_upper_threshold
        self.weak_lower_threshold = weak_lower_threshold
        self.strong_lower_threshold = strong_lower_threshold


class DetectorTrainer:
    pass

class ConstantThresholdDetectorTrainer(DetectorTrainer):
    class Strategy(Enum):
        SIGMA = "sigma"
        QUARTILE = "quartile"

    def get_detector(self, strategy, sample, weak_multiplier, strong_multiplier):
        if strategy == self.Strategy.SIGMA:
            return self._create_sigma_detector(sample, weak_multiplier, strong_multiplier)
        if strategy == self.Strategy.QUARTILE:
            return self._create_quartile_detector(sample, weak_multiplier, strong_multiplier)
        raise Exception("Unknown training strategy")
        # TODO: Raise customized exception

    def _create_sigma_detector(self, sample, weak_multiplier, strong_multiplier):
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
        STRATEGY = self.Strategy.QUARTILE

        q1, median, q3 = calculate_quartiles(sample)
        weak_upper_threshold, weak_lower_threshold = calculate_quartile_thresholds(q1, q3,
                weak_multiplier)
        strong_upper_threshold, strong_lower_threshold = calculate_quartile_thresholds(q1, q3,
                strong_multiplier)

        return Detector(STRATEGY, weak_multiplier, strong_multiplier,
                        weak_upper_threshold, strong_upper_threshold,
                        weak_lower_threshold, strong_lower_threshold)


def calculate_sigma(sample):
    if len(sample) < 2:
        raise Exception("Sample must have at least two elements")
    array = np.array(sample)
    return np.std(array, ddof=1)

def calculate_mean(sample):
    array = np.array(sample)
    return np.mean(array)

def calculate_sigma_thresholds(sigma, mean, multiplier):
    upper = mean + sigma * multiplier
    lower = mean - sigma * multiplier
    return upper, lower

def calculate_quartiles(sample):
    ''' Note that "quartiles" are calculated using 25th, 50th, and 75th percentile, and may differ than
    quartiles calculated manually.
    '''
    array = np.array(sample)
    return np.percentile(array, [25, 50, 75], interpolation='midpoint')

def calculate_quartile_thresholds(q1, q3, multiplier):
    iqr = q3 - q1
    upper = q3 + iqr * multiplier
    lower = q1 - iqr * multiplier
    return upper, lower


# TODO: Add descriptions for method arguments
# TODO: Add logging
