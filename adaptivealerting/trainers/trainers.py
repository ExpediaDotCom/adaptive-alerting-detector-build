import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

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
    array = np.array(sample)
    return np.percentile(array, [25, 50, 75], interpolation='midpoint')

def calculate_quartile_thresholds(q1, q3, multiplier):
    iqr = q3 - q1
    upper = q3 + iqr * multiplier
    lower = q1 - iqr * multiplier
    return upper, lower

