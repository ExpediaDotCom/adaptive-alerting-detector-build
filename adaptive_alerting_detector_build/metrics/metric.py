import requests
import pandas as pd
from adaptive_alerting_detector_build.datasources import datasource
from adaptive_alerting_detector_build.detectors import build_detector, DetectorClient
from adaptive_alerting_detector_build.profile.metric_profiler import build_profile

class Metric:

    def __init__(self, config, datasource_config, model_service_url=None):
        self.config = config
        self._datasource = datasource(datasource_config)
        self._detector_client = DetectorClient(model_service_url=model_service_url)
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
                detector.train(data=self.query())
                new_detector = self._detector_client.create_detector(
                    detector)
                self._detector_client.save_metric_detector_mapping(
                    new_detector.uuid, self)
                new_detectors.append(new_detector)
        return new_detectors


    def select_detectors(self):
        """
        TODO: Use metric profile data to determine which detectors to use
        """
        constant_threshold_detector = dict(
            type = "constant-detector",
            config = dict(
                hyperparameters =dict(
                    strategy="sigma", weak_multiplier=3.0, strong_multiplier=4.0
                )
            )
        )
        return [constant_threshold_detector]

    @property
    def sample_data(self):
        if not self._sample_data:
            self._sample_data = self.query()
        return self._sample_data

    @property
    def profile(self):
        if not self._profile:
            self._profile = build_profile(self.sample_data)
        return self._profile


"""
train interval will be dependent on profile attributes
no data - don't build a detector now
"""