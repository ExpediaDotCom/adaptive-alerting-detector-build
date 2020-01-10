from adaptive_alerting_detector_build.exceptions import AdaptiveAlertingDetectorBuildError


class _datasource:
    def __init__(self, **kwargs):
        pass

    def query(self):
        raise NotImplementedError


class DatasourceQueryException(AdaptiveAlertingDetectorBuildError):
    """Raised when query fails."""
