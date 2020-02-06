from .stationarity_types import StationarityReport


def print_stationarity_report(stationarity_report: StationarityReport):
    if stationarity_report:
        print('Annotated Results of Dickey-Fuller Test:')
        print(stationarity_report.adf_result_wrapper.pprints())
        print(stationarity_report.adf_summary)
