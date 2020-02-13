"""
Custom related field.  See https://github.com/genomoncology/related/blob/master/src/related/fields.py for examples.
"""
from attr import attrib, NOTHING
import pandas as pd
from related import _init_fields, to_dict

def TimeDelta(default=NOTHING, required=True, repr=True, cmp=True,
                 key=None):
    """
    Create new bool field on a model.
    :param default: any timedelta string
    :param bool required: whether or not the object is invalid if not provided.
    :param bool repr: include this field should appear in object's repr.
    :param bool cmp: include this field in generated comparison.
    :param string key: override name of the value when converted to dict.
    """
    default = _init_fields.init_default(required, default, None)
    validator = _init_fields.init_validator(required, pd._libs.tslibs.timedeltas.Timedelta)
    converter = pd.to_timedelta
    return attrib(default=default, converter=converter, validator=validator,
                  repr=repr, cmp=cmp, metadata=dict(key=key))

@to_dict.register(pd._libs.tslibs.timedeltas.Timedelta)
def _(obj, **kwargs):
    """
    Used for dict & json serialization
    """
    fields = {
        'days':'d', 
        'hours':'h', 
        'minutes':'m'
    }
    fmts = []
    for field, abbr in fields.items():
        val = getattr(obj.components,field)
        if val > 0:
            fmts.append(f"{val}{abbr}")
    return "".join(fmts) 
