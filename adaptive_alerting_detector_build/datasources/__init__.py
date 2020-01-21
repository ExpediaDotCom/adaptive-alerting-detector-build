from adaptive_alerting_detector_build.exceptions import (
    AdaptiveAlertingDetectorBuildError,
)
from .base import base_datasource, DatasourceQueryException
from ._graphite import graphite
from ._mock import mock


def datasource(datasource_config):
    """
    Datasource builder.  Config may vary per datasource.  Default type is 'graphite'.  
    """
    __datasource_type = (
        datasource_config["type"] if "type" in datasource_config else "graphite"
    )
    __datasource = None
    if __datasource_type == "graphite":
        __datasource = graphite(**datasource_config)
    elif __datasource_type == "mock":
        __datasource = mock(**datasource_config)
    else:
        raise AdaptiveAlertingDetectorBuildError(
            f"Unknown datasource type '{__datasource_type}'"
        )
    return __datasource
