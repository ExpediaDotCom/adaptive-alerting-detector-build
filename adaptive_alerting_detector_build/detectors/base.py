import related


@related.immutable
class DetectorUUID:
    uuid = related.UUIDField()


@related.mutable
class Detector:
    type = related.StringField()
    config = related.ChildField(object, key="detectorConfig")
    enabled = related.BooleanField(default=True)
    trusted = related.BooleanField(default=False)
    last_updated = related.DateTimeField(
        "%Y-%m-%d %H:%M:%S", required=False, key="lastUpdateTimestamp"
    )
    uuid = related.StringField(required=False)
    date_created = related.DateTimeField(required=False, key="dateCreated")
    created_by = related.StringField(required=False, key="createdBy")

    def train(self, data, *args, **kwargs):
        """
        TODO: Add metadata boolean that tells if the detector needs training.
        """
        raise NotImplementedError
