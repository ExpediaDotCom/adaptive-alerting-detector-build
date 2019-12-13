# from enum import Enum

# @attr.s
# class ConstantThreshold:
#     upperWeak = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(float)))
#     upperStrong = attr.ib()
#     train = attr.ib(validator=attr.validators.provides(ITrain))

#     @x.upperStrong
#     def check(self, attribute, value):
#         if self.upperWeak and attr.validators.instance_of
#             raise ValueError("x must be smaller or equal to 42"))

# {
#     "type": "constant-detector",
#     "detectorConfig": {
#         "hyperparams": {
#             "strategy": strategy,
#             "upper_weak_multiplier": upper_weak_multiplier,
#             "upper_strong_multiplier": upper_strong_multiplier
#         },
#         "trainingMetaData": {},
#         "params": {
#             "type": "RIGHT_TAILED",
#             "thresholds": {
#                 "upperWeak": upper_weak,
#                 "upperStrong": upper_strong
#                 }
#             }
#         },
#     "enabled": "true",
#     "lastUpdateTimestamp": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
#     "createdBy": app.config.get('model_username')
# }
