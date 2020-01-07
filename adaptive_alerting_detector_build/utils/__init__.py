import attr
import re


def validate(type, optional=False, pattern=None):

    validators = [attr.validators.instance_of(type)]

    if pattern:
        regex = re.compile(pattern)

        def pattern_validator(instance, attribute, val):
            if not val or not regex.match(val):
                raise ValueError(f"{attribute.name} must match pattern '{pattern}'")

        validators.append(pattern_validator)

    return attr.validators.optional(validators) if optional else validators


# def string(optional=False):
#     validator = attr.validators.optional(
#         isinstance(s, str)) if optional else is_string
#     return validator
