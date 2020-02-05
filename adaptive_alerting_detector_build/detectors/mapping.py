import related

from adaptive_alerting_detector_build.config import MODEL_SERVICE_USER
from adaptive_alerting_detector_build.detectors import DetectorUUID

@related.immutable
class DetectorMappingUser:
    id = related.StringField()

@related.immutable
class DetectorMappingOperandField:
    key = related.StringField()
    value = related.StringField()

@related.immutable
class DetectorMappingOperand:
    field = related.ChildField(DetectorMappingOperandField)

@related.immutable
class DetectorMappingExpression:
    operands = related.SequenceField(DetectorMappingOperand)
    operator = related.StringField(default="AND")
    

@related.immutable
class DetectorMapping:
    detector = related.ChildField(DetectorUUID)
    expression = related.ChildField(DetectorMappingExpression)
    fields = related.SequenceField(str)
    user = related.ChildField(DetectorMappingUser)

def build_metric_detector_mapping(detector_uuid, metric):
    operands = list()
    fields = list()
    for tag_key, tag_value in metric.config["tags"].items():
        operand = DetectorMappingOperand(
            field=DetectorMappingOperandField(
                key=tag_key,
                value=tag_value
            )
        )
        operands.append(operand)
        fields.append(tag_key)
    return DetectorMapping(**{
        "detector": {
            "uuid": detector_uuid
        },
        "expression": {
            "operands": operands,
            "operator": "AND"
        },
        "fields": fields,
        "user": {
            "id": MODEL_SERVICE_USER
        }
        })
