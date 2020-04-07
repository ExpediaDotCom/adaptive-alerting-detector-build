# All exceptions in this class should subclass from AdaptiveAlertingDetectorBuildError.


class AdaptiveAlertingDetectorBuildError(Exception):
    """Base class for all Adaptive Alerting Detector Build errors."""

    def __init__(self, msg=""):
        self.msg = msg
