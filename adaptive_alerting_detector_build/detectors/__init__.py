from .base import base_detector
from ._client import client
from ._constant_threshold import constant_threshold, constant_threshold_strategy
from adaptive_alerting_detector_build.exceptions import (
    AdaptiveAlertingDetectorBuildError,
)


def detector(metric, detector_config):
    """
    Detector builder.  Config may vary per detector.  Default type is 'constant-threshold'.  
    """
    __detector_type = (
        detector_config["type"] if "type" in detector_config else "constant-threshold"
    )
    __detector = None
    # TODO: add detector schema validation
    # Add elif for additional detector types
    if detector_config["type"] == "constant-threshold":
        __detector = constant_threshold(metric, detector_config)
    else:
        raise AdaptiveAlertingDetectorBuildError(
            f"Unknown detector type '{__detector_type}'"
        )
    return __detector
