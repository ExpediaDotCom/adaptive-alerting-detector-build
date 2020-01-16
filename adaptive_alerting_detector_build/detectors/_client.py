import logging
import requests
from datetime import datetime
import time

LOGGER = logging.getLogger(__name__)

class client:

    def __init__(self, url, **kwargs):
        self._url = url

    def search(self, metric_tags):
        pass

    # detectors can't be managed without looking up by a metric, so the only way to create a detector is to lookup the metric first and see that it doesn't exist.  If it exists,
    def create(self, detector_type, detectorConfig, createdBy, enabled=True, trusted=True):
        """

        If a detector already exists for metric, DetectorBuilderError is raised
        """
        data = {
            "type": detector_type,
            "trusted": trusted,
            "detectorConfig": detectorConfig,
            "enabled": enabled,
            "lastUpdateTimestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "createdBy": createdBy
        }
        response = requests.post(
            f"%{self._url}/modelservice/api/v2/detectors/",
            json=data,
        )
        response.raise_for_status()
        detector_uuid = response.text
        return detector_uuid


    # # pylint: disable-msg=too-many-arguments
    # def update_detector_thresholds(detector_uuid, upper_weak, upper_strong,
    #                             strategy, upper_weak_multiplier, upper_strong_multiplier):
    #     detector_data = update_detector_config_params(detector_uuid, upper_weak, upper_strong,
    #                                                 strategy, upper_weak_multiplier,
    #                                                 upper_strong_multiplier)
    #     detector_config = detector_data.get('detectorConfig')
    #     return detector_config


    # def get_detector_details(detector_uuid):
    #     response = requests.get(
    #         '%s/modelservice/api/v2/detectors/findByUuid?uuid=%s'
    #         % (app.config.get('model_service_host'), detector_uuid)
    #     )
    #     LOGGER.info('detector_url=%s', response.url)
    #     if response.status_code != 200:
    #         detector_data = {"type": "detector not found"}
    #         emit_fail_metrics('get_detector_by_uuid')
    #         return detector_data
    #     detector_data = response.json()
    #     emit_success_metrics('get_detector_by_uuid')
    #     return detector_data


    # # pylint: disable-msg=too-many-arguments
    # def update_detector_config_params(detector_uuid,
    #                                 upper_weak,
    #                                 upper_strong,
    #                                 strategy,
    #                                 upper_weak_multiplier,
    #                                 upper_strong_multiplier):
    #     detector_data = get_detector_details(detector_uuid)
    #     LOGGER.info('updating detector_id=%s', detector_uuid)
    #     detector_data['detectorConfig']['params']['thresholds']['upperWeak'] = upper_weak
    #     detector_data['detectorConfig']['params']['thresholds']['upperStrong'] = upper_strong
    #     detector_data['detectorConfig']['hyperparams']['strategy'] = strategy
    #     detector_data['detectorConfig']['hyperparams']['upper_weak_multiplier']\
    #         = upper_weak_multiplier
    #     detector_data['detectorConfig']['hyperparams']['upper_strong_multiplier']\
    #         = upper_strong_multiplier
    #     LOGGER.info('update data =%s', detector_data)
    #     response = requests.put(
    #         '%s/modelservice/api/v2/detectors?uuid=%s'
    #         % (app.config.get('model_service_host'), detector_uuid),
    #         json=detector_data
    #     )
    #     LOGGER.info('detector_update.status_code=%s', response.status_code)
    #     if response.status_code == 200:
    #         detector_data = get_detector_details(detector_uuid)
    #         emit_success_metrics('update_detector_thresholds')
    #     else:
    #         detector_data = {"type": "api failed"}
    #         emit_fail_metrics('update_detector_thresholds')
    #     return detector_data


    # def find_detector_uuid_by_tags(tags):
    #     response = requests.post(
    #         '%s/modelservice/api/detectorMappings/findMatchingByTags'
    #         % app.config.get('model_service_host'),
    #         json=[tags]
    #     )
    #     LOGGER.info('detector_url=%s', response.url)
    #     ids = response.json()['groupedDetectorsBySearchIndex'].get('0', [])
    #     detector_uuid = None
    #     if ids:
    #         if len(ids) > 1:
    #             LOGGER.warning(
    #                 'Received multiple detectors for tags. Will use last one. detectors=%s tags=%s',
    #                 ids,
    #                 tags
    #             )
    #             emit_fail_metrics('more_than_one_detectors_for_same_tags')
    #         detector_uuid = ids[-1].get('uuid')
    #     LOGGER.info('found detector_uuid=%s for tags=%s', detector_uuid, tags)
    #     return detector_uuid
            