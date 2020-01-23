import logging
import requests
import time
from .factory import create_detector
from .exceptions import DetectorBuilderError


LOGGER = logging.getLogger(__name__)


class DetectorBuilderClientError(DetectorBuilderError):
    """Base class for detector builder client errors."""


class DetectorClient:
    def __init__(self, url, **kwargs):
        self._url = url

    def get_detector(self, detector_uuid):
        response = requests.get(
            f"{self._url}/modelservice/api/v2/detectors/findByUuid?uuid={detector_uuid}"
        )
        response.raise_for_status()
        return create_detector(**response.json())

    def list_detectors(self, metric_tags):
        response = requests.post(
            f"{self._url}/modelservice/api/detectorMappings/findMatchingByTags",
            json=[metric_tags],
        )
        response.raise_for_status()
        detectors = []
        for detector_result in response.json():
            detectors.append(self.get_detector(detector_result["uuid"]))
        response.json()

    def create_detector(
        self, detector_type, detector_config, created_by, enabled=True, trusted=True
    ):
        """
        Detectors can't be managed without looking up by a metric, so the only way to
        create a detector is to lookup the metric first and see that it doesn't exist.
        If a detector already exists for metric, DetectorBuilderError is raised.
        """
        data = {
            "type": detector_type,
            "trusted": trusted,
            "detectorConfig": detector_config,
            "enabled": enabled,
            "lastUpdateTimestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "createdBy": created_by,
        }
        response = requests.post(
            f"{self._url}/modelservice/api/v2/detectors/", json=data,
        )
        response.raise_for_status()
        detector_uuid = response.text
        return self.get_detector(detector_uuid)

    def update_detector(self, detector_uuid, config=None, enabled=None, trusted=None):
        """
        * The service requires 'type' on update, but we treat it as immutable.
        * If values for 'detector_config', 'enabled', or 'trusted' are not passed, the
          current value is used.
        """
        current_detector = self.get_detector(detector_uuid)
        updated_config = config if config else current_detector.config
        updated_enabled = enabled if enabled else current_detector.enabled
        updated_trusted = trusted if trusted else current_detector.trusted
        data = {
            "detectorConfig": updated_config,
            "enabled": updated_enabled,
            "trusted": updated_trusted,
            "lastUpdateTimestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        }
        response = requests.post(
            f"{self._url}/modelservice/api/v2/detectors/", json=data, timeout=30
        )
        response.raise_for_status()
        detector_uuid = response.text
        return self.get_detector(detector_uuid)
