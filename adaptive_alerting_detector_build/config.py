import os
import uuid


LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

MODEL_SERVICE_USER = os.environ.get("MODEL_SERVICE_USER")

MODEL_SERVICE_URL = os.environ.get("MODEL_SERVICE_URL")

GRAPHITE_URL = os.environ.get("GRAPHITE_URL")

def get_datasource_config():
    if not GRAPHITE_URL:
        raise ValueError("GRAPHITE_URL not set.")
    return {
        "url": GRAPHITE_URL
    }