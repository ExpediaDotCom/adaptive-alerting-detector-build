"""Adaptive Alerting Detector Build

Creates, re-trains, and disables Adaptive Alerting detectors, based on the provided
JSON metrics configuration file.

Usage:
    adaptive-alerting build <json_config_file>...
    adaptive-alerting disable <json_config_file>...
    adaptive-alerting train <json_config_file>...
    adaptive-alerting diff <json_config_file_previous> <json_config_file_current> <output_file>
    adaptive-alerting -h | --help

Commands:
    build       builds new detectors for each metric
    train       trains existing detectors for each metric
    disable     disables detectors for each metric
    diff        show changes between config files versions

Options:
    json_config_file                One or more configuration files containing the metric configuration
    json_config_file_previous       Previous version of config file
    json_config_file_current        Current versoin of config file
    output_file                    Diff output file location
    -h --help                     Show this screen

Examples:
    adaptive-alerting build metrics.json

    adaptive-alerting disable metrics.json

    adaptive-alerting train metrics.json

    adaptive-alerting diff metrics_v1.json metrics_v2.json 

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


def disable_detectors_for_metric_configs(metric_configs):
    exit_code = 0
    for metric_config in metric_configs:
        metric = Metric(related.to_dict(metric_config), metric_config.datasource)
        try:
            disabled_detectors = metric.disable_detectors()
            for detector in disabled_detectors:
                logging.info(
                    f"Detector/Detector Mapping with UUID '{detector.uuid}' disabled."
                )
            if not disabled_detectors:
                logging.info(
                    f"No detectors to disable for metric '{metric_config.name}'"
                )
        except Exception as e:
            logging.exception(
                f"Exception {e.__class__.__name__} while disabling detectors for metric {metric_config.name}! Skipping!"
            )
            trace = traceback.format_exc()
            logging.debug(f"Traceback: {trace}")
            exit_code = 1
    return exit_code


def diff_metric_configs(previous_metric_configs, current_metric_configs):
    diff = {
        "added": [],
        "modified":[],
        "deleted":[]
    }
    previous_metric_config_keys = [i.tag_key for i in previous_metric_configs]
    previous_metric_json_configs = [related.to_json(i) for i in previous_metric_configs]
    current_metric_config_keys = [i.tag_key for i in current_metric_configs]
    for current_metric_config in current_metric_configs:
        if current_metric_config.tag_key not in previous_metric_config_keys:
            diff["added"].append(related.to_dict(current_metric_config))
        elif related.to_json(current_metric_config) not in previous_metric_json_configs:
            diff["modified"].append(related.to_dict(current_metric_config))
    for previous_metric_config in previous_metric_configs:
        if previous_metric_config.tag_key not in current_metric_config_keys:
            diff["deleted"].append(related.to_dict(previous_metric_config))
    return diff
        

def console_script_entrypoint():
    logging.basicConfig(level=logging.INFO)
    args = docopt(__doc__, version=__version__)
    exit_code = 0

    if args["disable"]:
        for json_config_file in args["<json_config_file>"]:
            logging.info("")
            metric_configs, exit_code = read_config_file(json_config_file)
            disable_exit_code = disable_detectors_for_metric_configs(metric_configs)
            if disable_exit_code > exit_code:
                exit_code = disable_exit_code
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

    elif args["diff"]:
        json_config_file_previous = args["<json_config_file_previous>"]
        json_config_file_current = args["<json_config_file_current>"]
        output_file = args["<output_file>"]
        logging.info(f"Comparing {json_config_file_previous} to {json_config_file_current}")
        previous_metric_configs, p_exit_code = read_config_file(json_config_file_previous)
        current_metric_configs, c_exit_code = read_config_file(json_config_file_current)
        exit_code = max(c_exit_code, p_exit_code)
        if exit_code == 0:
            diff = diff_metric_configs(previous_metric_configs, current_metric_configs)
            with open(output_file, "w") as output_file_handle:
                output_file_handle.write(json.dumps(diff, indent=4))
        logging.info("Done")

    sys.exit(exit_code)
