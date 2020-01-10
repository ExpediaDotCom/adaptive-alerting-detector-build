from adaptive_alerting_detector_build.datasources import graphite
import pandas as pd
import responses
import json


@responses.activate
def test_graphite_query():
    responses.add(responses.GET, "http://graphite/render?target=sumSeries(seriesByTag('role=my-app-web','what=elb_2xx'))&from=-168hours&until=now&format=json",
                    json=json.loads(open('tests/data/graphite_mock.json').read()),
                    status=200)
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={"role": "my-app-web", "what": "elb_2xx"}, 
        start="-168hours",
        end="now")
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)
    
@responses.activate
def test_graphite_query_with_interval():
    responses.add(responses.GET, "http://graphite/render?target=sumSeries(seriesByTag('role=my-app-web','what=elb_2xx'))|summarize('1min','sum')&from=-168hours&until=now&format=json",
                    json=json.loads(open('tests/data/graphite_mock.json').read()),
                    status=200)
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={"role": "my-app-web", "what": "elb_2xx"}, 
        start="-168hours",
        end="now",
        interval="1min")
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)