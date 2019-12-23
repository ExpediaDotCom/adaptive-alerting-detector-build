from adaptivealerting.detectors import base

class ConstantThresholdDetector(base.Detector):
    """Constant threshold detector that is used by Adaptive Alerting to find anomalies.

    Detector model contains thresholds for weak and strong anomalies.

    Parameters:

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



