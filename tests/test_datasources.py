from adaptive_alerting_detector_build.datasources import graphite
import pandas as pd
import responses
import json
from tests.conftest import GRAPHITE_MOCK_RESPONSE


@responses.activate
def test_graphite_query():
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('role=my-web-app','what=elb_2xx'))&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={"role": "my-web-app", "what": "elb_2xx"}, start="-168hours", end="now"
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)


@responses.activate
def test_graphite_query_with_function_tag():
    responses.add(
        responses.GET,
        "http://graphite/render?target=summarize(sumSeries(seriesByTag('role=my-web-app','what=elb_2xx')),'1min','sum',false)&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={
            "role": "my-web-app",
            "what": "elb_2xx",
            "function": "summarize(sumSeries(seriesByTag('role=my-web-app','what=elb_2xx')),'1min','sum',false)",
        },
        start="-168hours",
        end="now",
        interval="1min",
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)


@responses.activate
def test_graphite_query_with_interval():
    responses.add(
        responses.GET,
        "http://graphite/render?target=seriesByTag('role=my-web-app','what=elb_2xx')|summarize('1min','sum')&from=-168hours&until=now&format=json",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={"role": "my-web-app", "what": "elb_2xx"},
        start="-168hours",
        end="now",
        interval="1min",
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)

@responses.activate
def test_graphite_query_with_maxdatapoints():
    responses.add(
        responses.GET,
        "http://graphite/render?target=sumSeries(seriesByTag('role=my-web-app','what=elb_2xx'))&from=-168hours&until=now&format=json&maxDataPoints=10080",
        json=GRAPHITE_MOCK_RESPONSE,
        status=200,
    )
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={"role": "my-web-app", "what": "elb_2xx"}, start="-168hours", end="now", maxDataPoints=10080
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)


@responses.activate
def test_graphite_query_with_empty_response():
    responses.add(
        responses.GET,
        "http://graphite/render?target=seriesByTag('role=my-web-app','what=elb_2xx')|summarize('1min','sum')&from=-168hours&until=now&format=json",
        json=[],
        status=200,
    )
    graphite_datasource = graphite(url="http://graphite")
    df = graphite_datasource.query(
        tags={"role": "my-web-app", "what": "elb_2xx"},
        start="-168hours",
        end="now",
        interval="1min",
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)
