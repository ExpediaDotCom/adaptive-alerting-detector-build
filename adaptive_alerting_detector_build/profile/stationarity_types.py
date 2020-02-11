from dataclasses import dataclass
from typing import Dict

import pandas as pd

from .df_helper import convert_df_to_str


@dataclass
class AdfResultWrapper:
    adfstat: float
    pvalue: float
    usedlag: float
    nobs: float
    critvalues: Dict[str, float]
    icbest: float

    def pprints(self):
        dfoutput = pd.Series(
            [self.adfstat, self.pvalue, self.usedlag, self.nobs],
            index=[
                "Test Statistic",
                "p-value",
                "#Lags Used",
                "Number of Observations Used",
            ],
        )
        for key, value in self.critvalues.items():
            dfoutput["Critical Value (%s)" % key] = value
        return convert_df_to_str(dfoutput)


@dataclass
class StationarityResult:
    is_stationary: bool
    adf_result: AdfResultWrapper


@dataclass
class StationarityReport:
    adf_result_wrapper: AdfResultWrapper
    adf_summary: str
    p_value_display: str
    stationarity_display: str
    is_stationary: bool
    test_stat_display: str
