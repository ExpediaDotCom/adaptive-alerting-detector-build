import logging

from adaptive_alerting_detector_build.profile.seasonality_types import SeasonalityReport

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def print_seasonality_report(seasonality_report: SeasonalityReport):
    if seasonality_report:
        LOGGER.info("Annotated Results of seasonal Test:")
        LOGGER.info(seasonality_report.seasonality_display)
