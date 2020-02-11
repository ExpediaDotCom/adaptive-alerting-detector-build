import related
from . import Detector
from .exceptions import DetectorBuilderError


def get_detector_class(type):
    DETECTORS = {c.id: c for c in Detector.__subclasses__()}
    _detector_class = DETECTORS.get(type)
    if not _detector_class:
        raise DetectorBuilderError(f"Unknown detector type '{type}'")
    return _detector_class


def build_detector(type, config, enabled=True, trusted=False, **_ignored_args):
    DETECTORS = {c.id: c for c in Detector.__subclasses__()}
    _detector_class = DETECTORS.get(type)
    if not _detector_class:
        raise DetectorBuilderError(f"Unknown detector type '{type}'")
    _detector_config = related.to_model(_detector_class.config_class, config)
    return _detector_class(type, _detector_config, enabled, trusted)
