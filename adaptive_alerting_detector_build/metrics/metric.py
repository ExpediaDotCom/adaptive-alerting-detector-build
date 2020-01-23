import requests
import pandas as pd
from adaptive_alerting_detector_build.datasources import datasource
from adaptive_alerting_detector_build.detectors import DetectorClient

class Metric:

    def __init__(self, metric_config, datasource_config, model_service_url):
        self.metric_config = metric_config
        self._datasource = datasource(datasource_config)
        self._detector_model_client = DetectorClient(model_service_url)

    def query(self):
        return self._datasource.query(tags=self.metric_config["tags"])
