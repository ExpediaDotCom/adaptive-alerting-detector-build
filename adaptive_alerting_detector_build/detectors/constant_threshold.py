from adaptive_alerting_detector_build.detectors import base

class ConstantThresholdDetector(base.Detector):
    """Constant threshold detector that is used by Adaptive Alerting to find anomalies.

    Detector model contains thresholds for weak and strong anomalies.

    Parameters:

    """

    def __init__(self, build_strategy, weak_upper_threshold, strong_upper_threshold,
                 weak_lower_threshold, strong_lower_threshold):
        self.build_strategy = build_strategy
        self.weak_upper_threshold = weak_upper_threshold
        self.strong_upper_threshold = strong_upper_threshold
        self.weak_lower_threshold = weak_lower_threshold
        self.strong_lower_threshold = strong_lower_threshold

    def __str__(self):
        return f"Strategy: {self.build_strategy}, " + \
               f"Weak upper threshold: {self.weak_upper_threshold}, " + \
               f"Strong upper threshold: {self.strong_upper_threshold}, " + \
               f"Weak lower threshold: {self.weak_lower_threshold}, " + \
               f"Strong lower threshold: {self.strong_lower_threshold}"
