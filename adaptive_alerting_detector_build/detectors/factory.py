import related
from . import Detector
from .exceptions import DetectorBuilderError

def get_detector_class(type):
    DETECTORS = {c.id: c for c in Detector.__subclasses__()}
    _detector_class = DETECTORS.get(type)
    if not _detector_class:
        raise DetectorBuilderError(f"Unknown detector type '{type}'")
    return _detector_class


def from_json(payload):
    base_detector = related.from_json(payload, Detector)
    return build_detector(
        base_detector.type,
        base_detector.config,
        enabled=base_detector.enabled, 
        trusted=base_detector.trusted, 
        last_updated=base_detector.last_updated,
        uuid=base_detector.uuid,
        created_by=base_detector.created_by,
        meta=base_detector.meta)

def build_detector(type, config, enabled=True, trusted=False, 
    last_updated=None, uuid=None, created_by=None, meta=None):
    detector_class = get_detector_class(type)
    if not detector_class:
        raise DetectorBuilderError(f"Unknown detector type '{type}'")
    detector_config = related.to_model(detector_class.config_class, config)
    training_interval = getattr(detector_class, "training_interval", None)
    return detector_class(
        type=type, 
        config=detector_config, 
        enabled=enabled, 
        trusted=trusted, 
        training_interval=training_interval,
        last_updated=last_updated,
        uuid=uuid,
        created_by=created_by,
        meta=meta
    )