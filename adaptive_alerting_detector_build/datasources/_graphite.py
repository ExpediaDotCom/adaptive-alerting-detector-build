import requests
import pandas as pd
from adaptive_alerting_detector_build.datasources import (
    base_datasource,
    DatasourceQueryException,
)


class graphite(base_datasource):
    def __init__(self, url, **kwargs):
        self._url = url
        self._render_url = f"{url}/render"
        super(graphite, self).__init__(**kwargs)

    # how should nulls be treated?
    def query(self, tags, start="-168hours", end="now", interval=None, fn="sum"):
        try:
            tag_query = ",".join([f"'{k}={v}'" for k, v in sorted(tags.items())])
            query = f"seriesByTag({tag_query})"
            if fn == "sum":
                query = f"sumSeries({query})"
            if interval:
                query = f"{query}|summarize('{interval}','{fn}')"
            params = {"target": query, "from": start, "until": end, "format": "json"}
            response = requests.get(self._render_url, params=params, timeout=1)
            response.raise_for_status()
            data = map(
                lambda d: {"time": d[1], "value": d[0]},
                response.json()[0]["datapoints"],
            )
            df = pd.DataFrame(data, columns=["time", "value"])
            datetime_series = pd.to_datetime(df["time"], unit="s")
            datetime_index = pd.DatetimeIndex(datetime_series.values)
            df2 = df.set_index(datetime_index)
            df2.drop("time", axis=1, inplace=True)
            return df2
        except Exception as e:
            raise DatasourceQueryException(f"Error querying graphite. {e}")
