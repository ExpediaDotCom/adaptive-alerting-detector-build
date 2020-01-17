from .stationarity_types import AnnotatedStationarityResult


def print_annotated_stationarity_result(annotated_stationarity_result: AnnotatedStationarityResult):
    if annotated_stationarity_result:
        print('Annotated Results of Dickey-Fuller Test:')
        print(annotated_stationarity_result.adf_result_wrapper.pprints())
        print(annotated_stationarity_result.adf_summary)
