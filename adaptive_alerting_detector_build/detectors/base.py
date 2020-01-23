import related

@related.mutable
class DetectorBase:
    detector_type = related.StringField()
    config = related.ChildField(object)
    enabled = related.BooleanField(default=True)
    trusted = related.BooleanField(default=False)
    last_updated = related.DateTimeField("%Y-%m-%d %H:%M:%S", required=False)
    detector_uuid = related.StringField(required=False)

    def train_detector(self, data, *args, **kwargs):
        raise NotImplementedError
