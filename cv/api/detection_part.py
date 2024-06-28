from collections import defaultdict
import yaml

from .detection import DetectionResult
from config.colors import color_green
from config.config import config

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

class DetectionPart:

    def __init__(self, vehicle_model, detection_class):
        self.detection_class = detection_class.replace('part_detection_v2_', '')
        self.part_id = None
        self.part_name = None
        self.part_name_long = None
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup

        if self.inspection_enabled:
            part_details = vehicle_parts_lookup[vehicle_model].get(self.detection_class)
            if part_details is None:
                self.inspection_enabled = False
            else:
                self.part_id = part_details['part_number']
                self.part_name = part_details['part_name']
                self.part_name_long = part_details['part_name_long']

        # Predictions
        self.part_results_count = 0

        # Selection
        self.part_result = DetectionResult.MISSING
        self.part_pred = None # part number

    def get_part_result(self):
        if self.part_id is None:
            return None
        return {
            'part_id': self.part_id,
            'part_name': self.part_name,
            'part_name_long': self.part_name_long,
            'result': self.part_result,
            'part_pred': self.part_pred,
            'type': self.detection_class,
            'spec': self.part_id,
            'actual': self.part_pred,
            'key': self.part_name,
        }

    def update(self, part_detections, detection_groups):
        if not self.inspection_enabled:
            return        
        part_detection = max(part_detections, key=lambda detection: detection.confidence) if len(part_detections) > 0 else None

        if part_detection is None:
            return
                
        result = DetectionResult.OK
        self.part_results_count += 1
        part_detection.final_details.color = color_green
        part_detection.final_details.result = result
        part_detection.final_details.ignore = False
        if self.part_results_count >= RESULT_COUNT_THRESHOLD:
            self.part_pred = self.part_id
            self.part_result = result