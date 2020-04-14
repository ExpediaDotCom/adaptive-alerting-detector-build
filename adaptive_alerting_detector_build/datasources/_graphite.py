import requests
import pandas as pd
from adaptive_alerting_detector_build.datasources import (
    base_datasource,
    DatasourceQueryException,
)


class graphite(base_datasource):
    def __init__(self, url, headers={}, **kwargs):
        self._url = url
        self._headers = headers
        self._render_url = f"{url}/render"
        super(graphite, self).__init__(**kwargs)

    # how should nulls be treated?
    def query(self, tags, start="-168hours", end="now", interval=None, fn="sum"):
        try:
            tag_query = ",".join([f"'{k}={v}'" for k, v in sorted(tags.items())])
            query = f"seriesByTag({tag_query})"
            if "function" in tags:
                query = tags["function"]
            elif interval:
                query = f"{query}|summarize('{interval}','{fn}')"
            elif fn == "sum":
                query = f"sumSeries({query})"
            params = {"target": query, "from": start, "until": end, "format": "json"}
            response = requests.get(self._render_url, params=params, headers=self._headers, timeout=60)
            response.raise_for_status()
            response_list = response.json()
            data = list()
            if response_list:
                for datapoint in response.json()[0]["datapoints"]:
                    data.append({"time": datapoint[1], "value": datapoint[0]})
            df = pd.DataFrame(data, columns=["time", "value"])
            datetime_series = pd.to_datetime(df["time"], unit="s")
            datetime_index = pd.DatetimeIndex(datetime_series.values)
            df2 = df.set_index(datetime_index)
            df2.drop("time", axis=1, inplace=True)
            return df2
        except Exception as e:
            raise DatasourceQueryException(f"Error querying graphite. {e}")
