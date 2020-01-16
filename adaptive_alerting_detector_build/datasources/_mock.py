import requests
import pandas as pd
from adaptive_alerting_detector_build.datasources import base_datasource, DatasourceQueryException
import time




class mock(base_datasource):

    def __init__(self, data=list(range(0,168)), **kwargs):
        self._data = data
        super(mock, self).__init__(**kwargs)

    # how should nulls be treated?
    def query(self, tags):
        try:
            current_time = int(time.time())
            data = [{"time": current_time + (i*60), "value": d} for i,d in enumerate(self._data)]
            df = pd.DataFrame(data, columns=["time", "value"])
            datetime_series = pd.to_datetime(df['time'], unit='s')
            datetime_index = pd.DatetimeIndex(datetime_series.values)
            df2=df.set_index(datetime_index)
            df2.drop('time',axis=1,inplace=True)
            return df2
        except Exception as e:
            raise DatasourceQueryException(f"Error generating mock data. {e}")
        