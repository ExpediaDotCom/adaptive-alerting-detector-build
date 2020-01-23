from adaptive_alerting_detector_build.metrics import Metric
import pandas as pd
import responses
import json


@responses.activate
def test_new_trusted_metric_detector():
    responses.add(responses.GET, "http://graphite/render?target=sumSeries(seriesByTag('role=my-app-web','what=elb_2xx'))&from=-168hours&until=now&format=json",
                    json=json.loads(open('tests/data/graphite_mock.json').read()),
                    status=200)
    # TODO: graphite returns valid data
    # TODO: responses.add model service get detectors for metric (return none)
    # TODO: responses.add model service create detector / mapping

    metric_config = { 
        "tags": {
            "role": "my-app-web", 
            "what": "elb_2xx"
    }}
    datasource_config = {
        "url": "http://graphite"
    }
    test_metric = Metric(metric_config, datasource_config, model_service_url="http://modelservice")
    assert isinstance(test_metric, Metric)
    # detector_config={}
    # test_metric_detector = test_metric_detector(test_metric, detector_config)
    # test_metric_detector.train()
    # test_metric_detector.save()
    # assert test_metric_detector.state=="TRUSTED"

@responses.activate
def test_new_untrusted_metric_detector():
    # TODO: graphite returns insufficient data
    pass

@responses.activate
def test_update_untrusted_metric_detector_to_trusted():
    # TODO: graphite returns insufficient data
    pass
    
@responses.activate
def test_update_trusted_metric_to_untrusted():
    # TODO: responses.add model service get detectors for metric (return constant-threshold)
    # TODO: responses.add model service update detector
    pass

@responses.activate
def test_update_trusted_metric_detector():
    # TODO: responses.add model service get detectors for metric (return constant-threshold)
    # TODO: responses.add model service update detector
    pass

@responses.activate
def test_delete_metric():
    # TODO: responses.add model service get detectors for metric (return constant-threshold)
    # TODO: responses.add model service update detector
    pass