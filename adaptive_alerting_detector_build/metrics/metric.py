import datetime
from enum import unique, Enum
import related
import requests
from adaptive_alerting_detector_build.config import get_datasource_config
from adaptive_alerting_detector_build.datasources import datasource
from adaptive_alerting_detector_build.detectors import build_detector, DetectorClient
from adaptive_alerting_detector_build.profile.metric_profiler import build_profile


@unique
class MetricType(Enum):
    REQUEST_COUNT = "REQUEST_COUNT"
    ERROR_COUNT = "ERROR_COUNT"
    SUCCESS_RATE = "SUCCESS_RATE"
    LATENCY = "LATENCY"


@related.immutable
class MetricConfig:
    name = related.StringField()
    type = related.ChildField(MetricType)
    tags = related.ChildField(dict)
    description = related.StringField(required=False)
    datasource = related.ChildField(
        dict, default=get_datasource_config(), required=False
    )


class Metric:
    def __init__(
        self, config, datasource_config, model_service_url=None, model_service_user=None
    ):
        self.config = config
        self._datasource = datasource(datasource_config)
        self._detector_client = DetectorClient(
            model_service_url=model_service_url, model_service_user=model_service_user
        )
        self._sample_data = None
        self._profile = None

    def query(self):
        return self._datasource.query(tags=self.config["tags"])

    @property
    def detectors(self):
        # removed optimization due to possible consistancy issues
        # if not self._detectors:
        #     self._detectors = self._detector_client.list_detectors_for_metric(self.config["tags"])
        # return self._detectors
        return self._detector_client.list_detectors_for_metric(self.config["tags"])

    def build_detectors(self, selected_detectors=None):
        """
        Creates selected detectors if they don't exist in the service.
        """
        _selected_detectors = []
        if selected_detectors:
            _selected_detectors = selected_detectors
        else:
            _selected_detectors = self.select_detectors()
        existing_detector_types = [d.type for d in self.detectors]
        new_detectors = list()
        for selected_detector in _selected_detectors:
            if selected_detector["type"] not in existing_detector_types:
                detector = build_detector(**selected_detector)
                detector.train(data=self.query(), metric_type=self.config["type"])
                new_detector = self._detector_client.create_detector(detector)
                self._detector_client.save_metric_detector_mapping(
                    new_detector.uuid, self
                )
                new_detectors.append(new_detector)
        return new_detectors

    def delete_detectors(self):
        """
        Deletes all detectors and mappings for the metric.
        """
        deleted_detectors = []
        for detector in self.detectors:
            detector_mappings = self._detector_client.list_detector_mappings(
                detector.uuid
            )
            for detector_mapping in detector_mappings:
                self._detector_client.delete_metric_detector_mapping(
                    detector_mapping.id
                )
            self._detector_client.delete_detector(detector.uuid)
            deleted_detectors.append(detector)
        return deleted_detectors

    def select_detectors(self):
        """
        TODO: Use metric profile data to determine which detectors to use
        """
        constant_threshold_detector = dict(
            type="constant-detector",
            config=dict(
                hyperparams=dict(
                    strategy="sigma", 
                    lower_weak_multiplier=3.0, 
                    lower_strong_multiplier=4.0,
                    upper_weak_multiplier=3.0, 
                    upper_strong_multiplier=4.0
                )
            ),
        )
        return [constant_threshold_detector]

    def train_detectors(self):
        """
        Trains all detectors for the metric, if needed.
        """
        updated_detectors = []
        for detector in self.detectors:
            if detector.needs_training:
                detector.train(data=self.query(), metric_type=self.config["type"])
                updated_detector = self._detector_client.update_detector(detector)
                updated_detectors.append(updated_detector)
        return updated_detectors

    @property
    def sample_data(self):
        if self._sample_data is None:
            self._sample_data = self.query()
        return self._sample_data

    @property
    def profile(self):
        if not self._profile:
            self._profile = build_profile(self.sample_data)
        return self._profile
