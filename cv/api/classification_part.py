from collections import defaultdict
import yaml
import json
import logging

from .detection import DetectionResult
from config.colors import color_green, color_red
from config.config import config, get_vehicle_parts_lookup, part_group_names_lookup

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

class ClassificationPart:

    def __init__(self, vehicle_model, detection_class, artifact):
        vehicle_parts_lookup = get_vehicle_parts_lookup()
        
        self.artifact = artifact
        self.detection_class = detection_class.split('__')[-1]
        self.part_id = None
        self.part_number = None
        self.part_name = None
        self.part_name_long = None
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
                if self.is_group:
                    self.part_id = part_details['part_group']
                else:
                    self.part_id = part_details['part_number']
                self.part_number = part_details['part_number']
                self.part_name = part_details['part_name']
                self.part_name_long = part_details['part_name_long']
                self.missing_class_name = part_details.get('missing_class_name')

        # Predictions
        self.part_results_count = defaultdict(int)

        # Selection
        self.part_result = DetectionResult.MISSING
        self.part_pred = None # part number

        logger.info('Init classification: %s', {
            'vehicle_model': vehicle_model,
            'detection_class': self.detection_class,
            'part_id': self.part_id,
            'part_number': self.part_number,
            'part_name': self.part_name,
            'part_name_long': self.part_name_long,
            'is_group': self.is_group,
            'missing_class_name': self.missing_class_name,
            'is_miss_inspection': self.is_miss_inspection,
        })


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
            'part_name_long': ("MISS/" if self.is_miss_inspection else "") + self.part_name_long,
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
        logger.debug("Updating classification: %s", self.detection_class)

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
        logger.debug("Current result: pred_part=%s result=%s self.part_id=%s missing_class_name=%s is_miss_inspection=%s",
              pred_part, result, self.part_id, self.missing_class_name, self.is_miss_inspection)
        # Keep in OK state if already passed
        if not ALLOW_OK_TO_NG and self.part_result == DetectionResult.OK:
            result = DetectionResult.OK
            pred_part = self.part_pred
            logger.debug("Updated result: pred_part=%s result=%s", pred_part, result)
        logger.debug("Result counts: %s", self.part_results_count)
        self.part_results_count[(pred_part, result)] += 1
        part_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
        part_detection.final_details.result = result
        part_detection.final_details.ignore = False
        if len(self.part_results_count) > 0:
            result = aggregate_results(self.part_results_count)
            # result, result_count = sorted(self.part_results_count.items(), key=lambda x: x[1], reverse=True)[0]
            # if result_count >= RESULT_COUNT_THRESHOLD:
            if result is not None:
                self.part_pred = result[0]
                self.part_result = result[1]
                logger.debug("Final result: part_pred=%s self.part_result=%s", self.part_pred, self.part_result)
            else:
                logger.debug("Result is not available yet.")

        
