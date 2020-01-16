import attr
import json
import copy

from adaptive_alerting_detector_build.utils import json_serializer
# from adaptive_alerting_detector_build.metrics import metric

class base_detector:
    """Base class for detectors."""
    metric = None

    def __init__(self, metric, config):
        self.metric = metric
        # self.__config = {}
        self.config = self.builder(config)

    # @property
    # def config(self):
    #     __config = {}
    #     for key, value in self.config.items():
    #         if attr.has(value):
    #             __config[key] = attr.asdict(value)
    #         else:
    #             __config[key] = value
    #     return __config
        
    # @config.setter
    # def config(self, config):
    #     self.__config = self.builder(copy.deepcopy(self.__config).update(config))
    
    def json(self):
        return json.dumps(self.config)

    def builder(self, config):
        return config

    def train(self, data, *args, **kwargs):
        raise NotImplementedError

    def save(self):
        pass
