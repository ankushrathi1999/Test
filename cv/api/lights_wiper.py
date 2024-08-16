from collections import defaultdict
import yaml
import json
import logging

from .detection import DetectionResult
from config.colors import color_green, color_red
from config.config import config, get_vehicle_parts_lookup, part_group_names_lookup
from config.models import PartDetectionModel
from .classification_part import ClassificationPart

logger = logging.getLogger(__name__)

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')
ALLOW_OK_TO_NG = api_config.getboolean('allow_ok_to_ng')

def aggregate_results(result_counts):
    result_counts = sorted(result_counts.items(), key=lambda x: x[1], reverse=True)
    ok_counts = [res for res in result_counts if res[0][1] == DetectionResult.OK]
    if len(ok_counts) > 0 and ok_counts[0][1] >= RESULT_COUNT_THRESHOLD:
        return ok_counts[0][0]
    elif len(result_counts) > 0 and result_counts[0][1] >= RESULT_COUNT_THRESHOLD:
        return result_counts[0][0]
    return None

class LightsWiper:

    def __init__(self, vehicle_model, artifact):
        lights_class = PartDetectionModel.CLASS_lights.replace('part_detection_v2_', '')
        wiper_class = PartDetectionModel.CLASS_wiper.replace('part_detection_v2_', '')
        self.lights = ClassificationPart(vehicle_model, lights_class, artifact)
        self.wiper = ClassificationPart(vehicle_model, wiper_class, artifact)

    def get_part_results(self):
        return [self.lights.get_part_result(), self.wiper.get_part_result()]
     
    def update(self, left_detections, right_detections, detection_groups):      
        logger.debug("Updating classification for lights and wiper:")

        try:
            light_detections = [
                *[detection for detection in left_detections if detection.classification_details.class_name == 'SW_LGT'],
                *[detection for detection in right_detections if detection.classification_details.class_name == 'SW_LGT']
            ]
        except Exception as ex:
            logger.debug("Failed to filter light detections: %s", ex)
            light_detections = []
        try:
            wiper_detections = [
                *[detection for detection in left_detections if detection.classification_details.class_name == 'SW_WIP'],
                *[detection for detection in right_detections if detection.classification_details.class_name == 'SW_WIP']
            ]
        except Exception as ex:
            logger.debug("Failed to filter wiper detections: %s", ex)
            wiper_detections = []

        self.lights.update(light_detections, detection_groups)
        self.wiper.update(wiper_detections, detection_groups)