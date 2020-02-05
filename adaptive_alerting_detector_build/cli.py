"""Adaptive Alerting Detectors CLI Tool

Creates, re-trains or deletes Adaptive Alerting Constant Threshold detectors, based on the provided
JSON metrics configuration file.

Usage:
    adaptive-alerting build --datasource=url --aaservice=url --username=name [--weakmultiplier=number] [--strongmultiplier=number] <json_config>...
    adaptive-alerting delete --aaservice=url <json_config>...
    adaptive-alerting -h | --help

Commands:
    build       builds new detectors or re-trains existing detectors for the metric
    delete      deletes detectors for the metric

Options:
    --datasource=url        URL for the datasource
    --aaservice=url         URL for the Adaptive Alerting Model Service
    --username=name         Alias of the user that will be stored with the detector
    --weakmultiplier=num    The multiplication factor for weak anomalies [default: 3]
    --strongmultiplier=num  The multiplication factor for strong anomalies [default: 5]
    json_config             One or more configuration files containing the metric configuration
    -h --help               Show this screen

Examples:
    adaptive-alerting build --datasource=https://graphite.company.com --aaservice=https://adaptive-alerting.company.com/modelservice --username=msmith service-name.json

    adaptive-alerting build --datasource=https://graphite.company.com --aaservice=https://adaptive-alerting.company.com/modelservice --username=msmith service-name1.json service-name2.json

    adaptive-alerting delete --aaservice=https://adaptive-alerting.company.com service-name.json

"""

import logging
import json
import sys
import time
import requests
from docopt import docopt
from adaptive_alerting_detector_build.metrics import Metric
from adaptive_alerting_detector_build.detectors import create_detector


class Detector:
    def __init__(self, modelservice_url):
        self.modelservice_url = modelservice_url

    def create_mapping(self, detector_uuid, tags, user):
        operands = []
        for key, value in tags.items():
            operands.append({"field": {"key": key, "value": value}, "expression": None})

        mapping_data = {
            "detector": {"uuid": detector_uuid},
            "expression": {"operator": "AND", "operands": operands},
            "user": {"id": user},
        }

        response = requests.post(
            f"{self.modelservice_url}/api/detectorMappings", json=mapping_data,
        )
        response.raise_for_status()
        return response.text

    def update_detector(self, detector):
        uuid = detector["uuid"]
        data = {
            "uuid": uuid,
            "type": detector["type"],
            "trusted": detector["trusted"],
            "detectorConfig": detector["detectorConfig"],
            "enabled": detector["enabled"],
            "lastUpdateTimestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "createdBy": detector["createdBy"],
        }
        response = requests.put(
            f"{self.modelservice_url}/api/v2/detectors?uuid={uuid}", json=data
        )
        response.raise_for_status()

    def create_detector(self, detector_config, created_by, enabled=True, trusted=True):
        data = {
            "type": "constant-detector",
            "trusted": trusted,
            "detectorConfig": detector_config,
            "enabled": enabled,
            "lastUpdateTimestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "createdBy": created_by,
        }
        response = requests.post(
            f"{self.modelservice_url}/api/v2/detectors/", json=data,
        )
        response.raise_for_status()
        detector_uuid = response.text
        return detector_uuid

    def get_detector_by_uuid(self, detector_uuid):
        response = requests.get(
            f"{self.modelservice_url}/api/v2/detectors/findByUuid?uuid={detector_uuid}"
        )
        response.raise_for_status()
        return response.json()

    def get_detector_by_tags(self, tags):
        # TODO: Handle case of more than one detector returned
        detectors = self.list_detectors(tags)

        if len(detectors["groupedDetectorsBySearchIndex"]) > 0:
            detector_uuid = detectors["groupedDetectorsBySearchIndex"]["0"][0]["uuid"]
            return self.get_detector_by_uuid(detector_uuid)

        return None

    def list_detectors(self, metric_tags):
        response = requests.post(
            f"{self.modelservice_url}/api/detectorMappings/findMatchingByTags",
            json=[metric_tags],
        )
        response.raise_for_status()
        return response.json()


def train_sigma_detector(sample, weak_multiplier, strong_multiplier):
    detector_config = {
        "training_metadata": {
            "strategy": "sigma",
            "weak_multiplier": weak_multiplier,
            "strong_multiplier": strong_multiplier,
        }
    }

    ct_detector = create_detector("constant_threshold", detector_config)
    ct_detector.train(sample)

    detector_config = {
        "hyperparams": {
            "strategy": "sigma",
            "upper_weak_multiplier": weak_multiplier,
            "upper_strong_multiplier": strong_multiplier,
        },
        "trainingMetaData": {},
        "params": {
            "type": "RIGHT_TAILED",
            "thresholds": {
                "upperWeak": ct_detector.config.hyperparameters.weak_upper_threshold,
                "upperStrong": ct_detector.config.hyperparameters.strong_upper_threshold,
            },
        },
    }
    return detector_config


def get_metric(metric_config, datasource_url, model_service_url):
    datasource_config = {"url": datasource_url}
    metric_svc = Metric(metric_config, datasource_config, model_service_url)
    metric_data = metric_svc.query()
    metric_no_nulls = metric_data.dropna(axis=0, how="any", inplace=False)
    return metric_no_nulls["value"].values.tolist()


def main():

    logging.basicConfig(level=logging.INFO)

    # command line arguments
    ARGS = docopt(__doc__)

    EXITCODE = 0

    detector_svc = Detector(ARGS["--aaservice"])

    if ARGS["delete"]:
        logging.info("Delete feature is not yet implemented.")
        EXITCODE = 2

    elif ARGS["build"]:
        for config_file in ARGS["<json_config>"]:
            logging.info("")
            logging.info(f"Processing configuration file: {config_file}")

            metric_config = {}
            try:
                metric_config = json.loads(open(config_file).read())
                logging.info(f"{json.dumps(metric_config)}")

                # get metric data from source
                metric_values = get_metric(
                    metric_config, ARGS["--datasource"], ARGS["--aaservice"]
                )

                # train detector
                detector_config = train_sigma_detector(
                    metric_values, ARGS["--weakmultiplier"], ARGS["--strongmultiplier"]
                )

                # search for existing mapping/detector
                detector = detector_svc.get_detector_by_tags(metric_config["tags"])

                if detector:
                    # detector and mapping exists; update only
                    # TODO: Only update if different
                    detector["detectorConfig"] = detector_config
                    detector_svc.update_detector(detector)
                    logging.info(f"Detector with UUID {detector['uuid']} updated")

                else:
                    # create new detector and mapping
                    uuid = detector_svc.create_detector(
                        detector_config, ARGS["--username"], enabled=True, trusted=True,
                    )
                    logging.info(f"New detector created with UUID: {uuid}")

                    mapping = detector_svc.create_mapping(
                        uuid, metric_config["tags"], ARGS["--username"]
                    )
                    logging.info(f"New mapping created with UUID: {mapping}")

            except FileNotFoundError as e:
                logging.exception(f"Error reading config file! Skipping!")
                EXITCODE = 1
            except json.decoder.JSONDecodeError as e:
                logging.exception(f"Error parsing config file! Skipping!")
                EXITCODE = 1

        logging.info("Done")

    sys.exit(EXITCODE)


