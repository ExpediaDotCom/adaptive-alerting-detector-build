# from abc import ABCMeta, abstractmethod
import attr
from adaptivealerting.utils import validate
from types import FunctionType

# from adaptivealerting.detectors import model


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
