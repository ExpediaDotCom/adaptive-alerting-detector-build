#!/usr/bin/env python3

"""Adaptive Alerting Detectors CLI Tool

Creates, re-trains or deletes Adaptive Alerting detectors, based on the provided JSON
metrics configuration file.

Usage:
    adaptive-alerting.py build --datasource=url --aaservice=url <json_config>...
    adaptive-alerting.py delete --aaservice=url <json_config>...
    adaptive-alerting.py -h | --help

Commands:
    build       builds new detectors or re-trains existing detectors for the metric
    delete      deletes detectors for the metric

Options:
    --datasource=url    URL for the datasource
    --aaservice=url     URL for the Adaptive Alerting service
    json_config         One or more configuration files containing the metric configuration
    -h --help           Show this screen

Examples:
    adaptive-alerting.py build --datasource=https://graphite.prod.com --aaservice=https://adaptive-alerting.prod.com service-name.json

    adaptive-alerting.py build --datasource=https://graphite.prod.com --aaservice=https://adaptive-alerting.prod.com service-name1.json service-name2.json

    adaptive-alerting.py delete --aaservice=https://adaptive-alerting.prod.com service-name.json 

"""

import logging
import json
from docopt import docopt


def main():

    logging.basicConfig(level=logging.INFO)

    # command line arguments
    ARGS = docopt(__doc__)
    logging.info(ARGS)


if __name__ == "__main__":

    main()
