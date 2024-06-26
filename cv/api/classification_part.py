from collections import defaultdict
import yaml
import json

from .detection import DetectionResult
from config.colors import color_green, color_red
from config.config import config

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')
ALLOW_OK_TO_NG = api_config.getboolean('allow_ok_to_ng')

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

with open('./config/part_group_names.json') as x:
    part_group_names_lookup = json.load(x)

class ClassificationPart:

    def __init__(self, vehicle_model, detection_class, artifact):
        self.artifact = artifact
        self.detection_class = detection_class.replace('part_detection_v2_', '')
        self.part_id = None
        self.part_number = None
        self.part_name = None
        self.is_group = False
        self.missing_class_name = None
        self.is_miss_inspection = False
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup

        if self.inspection_enabled:
            part_details = vehicle_parts_lookup[vehicle_model].get(self.detection_class)
            if part_details is None:
                self.inspection_enabled = False
            else:
                self.is_group = part_details.get('is_group') is True
                self.is_miss_inspection = part_details.get('is_miss') is True
                print(vehicle_model, detection_class, part_details)
                if self.is_group:
                    self.part_id = part_details['part_group']
                else:
                    self.part_id = part_details['part_number']
                self.part_number = part_details['part_number']
                self.part_name = part_details['part_name']
                self.missing_class_name = part_details.get('missing_class_name')

        # Predictions
        self.part_results_count = defaultdict(int)

        # Selection
        self.part_result = DetectionResult.MISSING
        self.part_pred = None # part number

    def get_part_result(self):
        if self.part_id is None:
            return None
        if self.is_group:
            spec = part_group_names_lookup.get(self.part_id, self.part_id)
            actual = part_group_names_lookup.get(self.part_pred, self.part_pred)
        elif self.is_miss_inspection:
            spec = None
            actual = self.part_pred if self.part_pred != self.missing_class_name else None
        else:
            spec = self.part_id
            actual = self.part_pred

        return {
            'part_id': self.part_number,
            'part_name': self.part_name,
            'result': self.part_result,
            'part_pred': self.part_pred,
            'type': self.detection_class,
            'spec': spec,
            'actual': actual,
            'key': self.part_name,
        }

    def update(self, part_detections, detection_groups):
        if not self.inspection_enabled:
            return        
        part_detection = max(part_detections, key=lambda detection: detection.confidence) if len(part_detections) > 0 else None

        if part_detection is None:
            return
                
        pred_part = part_detection.classification_details.part_number
        if (self.missing_class_name and pred_part == self.missing_class_name):
            result = DetectionResult.OK if self.is_miss_inspection else DetectionResult.MISSING
        elif (self.missing_class_name and self.is_miss_inspection):
            result = DetectionResult.INCORRECT_PART
        else:
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

        