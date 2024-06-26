import yaml
import json

from .detection import DetectionResult
from .classification_part import ClassificationPart
from config.models import PartClassificationModel, PartDetectionModel
from config.colors import color_green, color_red
from config.config import config

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')
ALLOW_OK_TO_NG = api_config.getboolean('allow_ok_to_ng')

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

with open('./config/part_group_names.json') as x:
    part_group_names_lookup = json.load(x)

class SteeringCover(ClassificationPart):

    def __init__(self, vehicle_model, detection_class):
        super().__init__(vehicle_model, detection_class)
        self.key_detecton_count = 0

    def update(self, part_detections, detection_groups):
        if not self.inspection_enabled:
            return        
        key_detections = detection_groups.get(PartDetectionModel.CLASS_key, [])
        if len(key_detections) > 0:
            self.key_detecton_count += 1
        is_key_present = self.key_detecton_count >= RESULT_COUNT_THRESHOLD

        part_detection = max(part_detections, key=lambda detection: detection.confidence) if len(part_detections) > 0 else None
        if part_detection is None:
            return
                
        pred_part_group = part_detection.classification_details.part_number
        pred_part = PartClassificationModel.get_part_number_steering_cover(pred_part_group, is_key_present, self.artifact.vehicle_category)
        result = DetectionResult.OK if pred_part == self.part_id else DetectionResult.INCORRECT_PART
        # Keep in OK state if already passed
        if not ALLOW_OK_TO_NG and self.part_result == DetectionResult.OK:
            result = DetectionResult.OK
            pred_part = self.part_pred
        self.part_results_count[(pred_part, result)] += 1
        part_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
        part_detection.final_details.result = result
        part_detection.final_details.ignore = False
        if len(self.part_results_count) > 0:
            result, result_count = sorted(self.part_results_count.items(), key=lambda x: x[1], reverse=True)[0]
            if result_count >= RESULT_COUNT_THRESHOLD:
                self.part_pred = result[0]
                self.part_result = result[1]