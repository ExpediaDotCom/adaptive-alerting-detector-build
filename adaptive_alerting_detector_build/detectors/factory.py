# from adaptive_alerting_detector_build import detectors
from . import DetectorBase
from .exceptions import DetectorBuilderError



def create_detector(detector_type, config, enabled=True, trusted=False, **_ignored_args):
    DETECTORS = {c.id: c for c in DetectorBase.__subclasses__()}
    print("DETECTORS",DETECTORS)
    _detector_class = DETECTORS.get(detector_type)
    if not _detector_class:
        raise DetectorBuilderError(f"Unknown detector type '{detector_type}'")
    _detector_config = _detector_class.config_class(config)
    return _detector_class(detector_type, _detector_config, enabled, trusted)
