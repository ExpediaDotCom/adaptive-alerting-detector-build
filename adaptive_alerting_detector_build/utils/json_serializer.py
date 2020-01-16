""" Module that monkey-patches the json module when it's imported so
JSONEncoder.default() automatically checks to see if the object being encoded
is an instance of an Enum type and, if so, returns its name.
https://stackoverflow.com/questions/36699512/is-it-possible-to-dump-an-enum-in-json-without-passing-an-encoder-to-json-dumps
"""
from enum import Enum
from json import JSONEncoder

_saved_default = JSONEncoder().default  # Save default method.


def _new_default(self, obj):
    if isinstance(obj, Enum):
        return obj.value  # Could also be obj.value
    else:
        return _saved_default


JSONEncoder.default = _new_default  # Set new default method.
