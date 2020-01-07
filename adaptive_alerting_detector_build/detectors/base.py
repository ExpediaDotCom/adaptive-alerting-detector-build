# from abc import ABCMeta, abstractmethod
import attr
from adaptive_alerting_detector_build.utils import validate
from types import FunctionType

# from adaptive_alerting_detector_build.detectors import model


@attr.s
class BaseDetector:
    name = attr.ib(validator=validate(str))
    # type = attr.ib(validator=attr.validators.in_(type))
    train = attr.ib(validator=validate(FunctionType))


# @
# class DetectorModel:
# """

# """

#     def __init__(self, name: str, type: DetectorType, datasource: ):
#         self.name = name
#         self.type = type
#         self.datasource = datasource
