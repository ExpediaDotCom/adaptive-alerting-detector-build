import datetime
import related
from related import to_dict
from adaptive_alerting_detector_build.utils.fields import TimeDelta

@related.immutable
class DetectorMeta:
    date_created = related.DateTimeField(required=False, key="dateCreated")


@related.immutable
class DetectorUUID:
    uuid = related.UUIDField()


@related.mutable
class Detector:
    type = related.StringField()
    config = related.ChildField(object, key="detectorConfig")
    enabled = related.BooleanField(default=True)
    trusted = related.BooleanField(default=False)
    training_interval = TimeDelta(default="0")
    last_updated = related.DateTimeField(
        "%Y-%m-%d %H:%M:%S", required=False, key="lastUpdateTimestamp"
    )
    uuid = related.StringField(required=False)
    created_by = related.StringField(required=False, key="createdBy")
    meta = related.ChildField(DetectorMeta, required=False)

    def train(self, data, *args, **kwargs):
        """
        TODO: Add metadata boolean that tells if the detector needs training.
        """
        raise NotImplementedError

    @property
    def minutes_since_created(self):
        if self.meta and self.meta.date_created:
            created_timedelta = (datetime.datetime.utcnow() - self.meta.date_created)
            return round(created_timedelta.total_seconds()/60)

    @property
    def minutes_since_trained(self):
        if self.last_updated:
            trained_timedelta = (datetime.datetime.utcnow() - self.last_updated)
            return round(trained_timedelta.total_seconds()/60)

    @property
    def needs_training(self):
        _needs_training = False
        training_interval_minutes = round(self.training_interval.total_seconds() / 60)
        if training_interval_minutes == 0:
            pass
        elif not self.uuid:
            _needs_training = True
        elif self.minutes_since_trained and self.minutes_since_trained > training_interval_minutes:
            _needs_training = True
        return _needs_training