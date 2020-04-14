import os
import uuid
from .exceptions import AdaptiveAlertingDetectorBuildError

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

MODEL_SERVICE_USER = os.environ.get("MODEL_SERVICE_USER")

MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL")

GRAPHITE_URL = os.environ.get("GRAPHITE_URL")

GRAPHITE_HEADERS = os.environ.get("GRAPHITE_HEADERS")


def get_datasource_config():
    """
    Graphite headers can be configured using enironment variables prefixed with 'GRAPHITE_HEADER_'
    Two environment variables are needed for each header key / value.  The environment variable 
    with the header's value should have the same name as the key's variable but end with '_VALUE'

    For example:

        GRAPHITE_HEADER_METRICTANK="x-org-id"
        GRAPHITE_HEADER_METRICTANK_VALUE="1"

    Has header:

        "x-org-id: 1"

    """
    if not GRAPHITE_URL:
        raise ValueError("GRAPHITE_URL not set.")
    graphite_config = {"url": GRAPHITE_URL, "headers": {}}
    for k, v in os.environ.items():
        if not k.startswith("GRAPHITE_HEADER_") or k.endswith("_VALUE"):
            continue
        header_name = v
        header_value = os.environ.get(f"{k}_VALUE")
        if not header_value:
            raise AdaptiveAlertingDetectorBuildError("Found Env Variable {k}, but no value for '{k}_VALUE'.")
        graphite_config["headers"][header_name] = header_value
    return graphite_config
