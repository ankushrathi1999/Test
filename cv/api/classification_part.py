from collections import defaultdict
import yaml

from .detection import DetectionResult
from config.colors import color_green, color_red

RESULT_COUNT_THRESHOLD = 2

with open('./config/vehicle_parts_new.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

class ClassificationPart:

    def __init__(self, vehicle_model, detection_class):
        self.detection_class = detection_class.replace('part_detection_', '')
        self.part_id = None
        self.part_name = None
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup

        if self.inspection_enabled:
            part_details = vehicle_parts_lookup[vehicle_model].get(self.detection_class)
            if part_details is None:
                self.inspection_enabled = False
            else:
                self.part_id = part_details['part_number']
                self.part_name = part_details['part_name']

        # Predictions
        self.part_results_count = defaultdict(int)

        # Selection
        self.part_result = DetectionResult.MISSING
        self.part_pred = None # part number

    def get_part_result(self):
        if self.part_id is None:
            return None
        return {
            'part_id': self.part_id,
            'part_name': self.part_name,
            'result': self.part_result,
            'part_pred': self.part_pred,
            'type': self.detection_class,
            'spec': self.part_id,
            'actual': self.part_pred,
            'key': self.part_name,
        }

    def update(self, part_detections):
        # print("Classification update", self.detection_class)
        if not self.inspection_enabled:
            return        
        part_detection = max(part_detections, key=lambda detection: detection.confidence) if len(part_detections) > 0 else None

        if part_detection is None:
            return
                
        pred_part = part_detection.classification_details.part_number
        result = DetectionResult.OK if pred_part == self.part_id else DetectionResult.INCORRECT_PART
        self.part_results_count[(pred_part, result)] += 1
        part_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
        part_detection.final_details.result = result
        part_detection.final_details.ignore = False
        if len(self.part_results_count) > 0:
            result, result_count = sorted(self.part_results_count.items(), key=lambda x: x[1], reverse=True)[0]
            if result_count >= RESULT_COUNT_THRESHOLD:
                self.part_pred = result[0]
                self.part_result = result[1]