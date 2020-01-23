import attr
import uuid

from adaptive_alerting_detector_build.utils.attrs import validate


@attr.s
class DetectorBase:
    detector_type = attr.ib(validator=validate(str))
    config = attr.ib()
    enabled = attr.ib(default=True, validator=validate(bool))
    trusted = attr.ib(default=False, validator=validate(bool))
    last_updated = attr.ib(default=None, validator=validate(str, optional=True))
    detector_uuid = attr.ib(default=None, validator=validate(str, optional=True))

    # @classmethod
    # def get_instance(cls, string):
    #     return next(c for c in cls.__subclasses__() if c.__name__.lower() == string)()

    def train_detector(self, data, *args, **kwargs):
        raise NotImplementedError
 