import logging

from .stationarity_types import StationarityReport

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def print_stationarity_report(stationarity_report: StationarityReport):
    if stationarity_report:
        LOGGER.info('Annotated Results of Dickey-Fuller Test:')
        LOGGER.info(stationarity_report.adf_result_wrapper.pprints())
        LOGGER.info(stationarity_report.adf_summary)
