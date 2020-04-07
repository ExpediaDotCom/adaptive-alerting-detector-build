"""Adaptive Alerting Detector Build

Creates, re-trains, and deletes Adaptive Alerting detectors, based on the provided
JSON metrics configuration file.

Usage:
    adaptive-alerting build <json_config_file>...
    adaptive-alerting delete <json_config_file>...
    adaptive-alerting train <json_config_file>...
    adaptive-alerting -h | --help

Commands:
    build       builds new detectors for each metric
    train       trains existing detectors for each metric
    delete      deletes detectors for each metric

Options:
    json_config_file          One or more configuration files containing the metric configuration
    -h --help               Show this screen

Examples:
    adaptive-alerting build metrics.json

    adaptive-alerting train metrics.json

    adaptive-alerting delete metrics.json

"""

from docopt import docopt
import logging
import json
import related
import sys
import traceback

from .exceptions import AdaptiveAlertingDetectorBuildError
from .metrics import Metric, MetricConfig
from . import __version__


LOGGER = logging.getLogger(__name__)


def read_config_file(json_config_file_path):
    metric_configs = list()
    exit_code = 0
    try:
        logging.info(f"Reading configuration file: {json_config_file_path}")
        with open(json_config_file_path) as json_config_file:
            raw_metric_configs = json.loads(json_config_file.read())
            if not isinstance(raw_metric_configs, list):
                raise ValueError()
            for raw_metric_config in raw_metric_configs:
                metric_config = related.to_model(MetricConfig, raw_metric_config)
                metric_configs.append(metric_config)
    except ValueError as e:
        logging.exception(
            f"Exception {e.__class__.__name__} while reading config file '{e}'! Skipping!"
        )
        exit_code = 1
    except Exception as e:
        logging.exception(
            f"Exception {e.__class__.__name__} while reading config file '{json_config_file_path}'! Skipping!"
        )
        trace = traceback.format_exc()
        logging.debug(f"Traceback: {trace}")
        exit_code = 1
    return (metric_configs, exit_code)


def build_detectors_for_metric_configs(metric_configs):
    exit_code = 0
    for metric_config in metric_configs:
        metric = Metric(related.to_dict(metric_config), metric_config.datasource)
        try:
            new_detectors = metric.build_detectors()
            for detector in new_detectors:
                logging.info(
                    f"New '{detector.type}' detector created with UUID: {detector.uuid}"
                )
            if not new_detectors:
                logging.info(f"No detectors built for metric '{metric_config.name}'")
        except AdaptiveAlertingDetectorBuildError as e:
            logging.warning(
                f"Unable to train detector for metric '{metric_config.name}',  {e.msg}! Skipping!"
            )                
        except Exception as e:
            logging.exception(
                f"Exception {e.__class__.__name__} while creating detector for metric {metric_config.name}! Skipping!"
            )
            trace = traceback.format_exc()
            logging.debug(f"Traceback: {trace}")
            exit_code = 1
    return exit_code


def train_detectors_for_metric_configs(metric_configs):
    exit_code = 0
    for metric_config in metric_configs:
        metric = Metric(related.to_dict(metric_config), metric_config.datasource)
        try:
            updated_detectors = []
            for detector in metric.detectors:
                if detector.needs_training:
                    detector.train(data=metric.query(), metric_type=metric.config["type"])
                    updated_detector = metric._detector_client.update_detector(detector)
                    updated_detectors.append(updated_detector)
                    logging.info(
                        f"Trained '{detector.type}' detector with UUID: {detector.uuid}"
                    )
                else:
                    logging.info(
                        f"Training not required for '{detector.type}' detector with UUID: {detector.uuid}"
                    )
        except AdaptiveAlertingDetectorBuildError as e:
            logging.error(
                f"Unable to train detector for metric '{metric_config.name}',  {e.msg}! Skipping!"
            )     
            exit_code = 0
        except Exception as e:
            logging.exception(
                f"Exception {e.__class__.__name__} while training detector(s) for metric {metric_config.name}! Skipping!"
            )
            trace = traceback.format_exc()
            logging.debug(f"Traceback: {trace}")
            exit_code = 1
    return exit_code


def delete_detectors_for_metric_configs(metric_configs):
    exit_code = 0
    for metric_config in metric_configs:
        metric = Metric(related.to_dict(metric_config), metric_config.datasource)
        try:
            deleted_detectors = metric.delete_detectors()
            for detector in deleted_detectors:
                logging.info(
                    f"Detector/Detector Mapping with UUID '{detector.uuid}' deleted."
                )
            if not deleted_detectors:
                logging.info(
                    f"No detectors to delete for metric '{metric_config.name}'"
                )
        except Exception as e:
            logging.exception(
                f"Exception {e.__class__.__name__} while deleting detectors for metric {metric_config.name}! Skipping!"
            )
            trace = traceback.format_exc()
            logging.debug(f"Traceback: {trace}")
            exit_code = 1
    return exit_code


def console_script_entrypoint():
    logging.basicConfig(level=logging.INFO)
    args = docopt(__doc__, version=__version__)
    exit_code = 0

    if args["delete"]:
        for json_config_file in args["<json_config_file>"]:
            logging.info("")
            metric_configs, exit_code = read_config_file(json_config_file)
            delete_exit_code = delete_detectors_for_metric_configs(metric_configs)
            if delete_exit_code > exit_code:
                exit_code = delete_exit_code
            logging.info("Done")

    elif args["build"]:
        for json_config_file in args["<json_config_file>"]:
            logging.info("")
            metric_configs, exit_code = read_config_file(json_config_file)
            build_exit_code = build_detectors_for_metric_configs(metric_configs)
            if build_exit_code > exit_code:
                exit_code = build_exit_code
            logging.info("Done")

    elif args["train"]:
        for json_config_file in args["<json_config_file>"]:
            logging.info("")
            metric_configs, exit_code = read_config_file(json_config_file)
            train_exit_code = train_detectors_for_metric_configs(metric_configs)
            if train_exit_code > exit_code:
                exit_code = train_exit_code
            logging.info("Done")
    sys.exit(exit_code)
