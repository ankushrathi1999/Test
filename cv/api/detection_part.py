import logging

from .detection import DetectionResult
from config.colors import color_green
from config.config import config, get_vehicle_parts_lookup

logger = logging.getLogger(__name__)

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')

class DetectionPart:

    def __init__(self, vehicle_model, detection_class):
        vehicle_parts_lookup = get_vehicle_parts_lookup()
        
        self.detection_class = detection_class.split('__')[-1]
        self.part_id = None
        self.part_name = None
        self.part_name_long = None
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup
        print("D1:", len(vehicle_parts_lookup), vehicle_model, vehicle_model in vehicle_parts_lookup)

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

        logger.info('Init detection: %s', {
            'vehicle_model': vehicle_model,
            'detection_class': self.detection_class,
            'part_id': self.part_id,
            'part_name': self.part_name,
            'part_name_long': self.part_name_long,
        })

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
        logger.debug("Updating detection: %s", self.detection_class)

        part_detection = max(part_detections, key=lambda detection: detection.confidence) if len(part_detections) > 0 else None
        if part_detection is None:
            return
        
        logger.debug("Result counts: %s", self.part_results_count)
        result = DetectionResult.OK
        self.part_results_count += 1
        part_detection.final_details.color = color_green
        part_detection.final_details.result = result
        part_detection.final_details.ignore = False
        if self.part_results_count >= RESULT_COUNT_THRESHOLD:
            self.part_pred = self.part_id
            self.part_result = result
            logger.debug("Final result: part_pred=%s part_result=%s", self.part_pred, self.part_result)
        else:
            logger.debug("Result is not available yet.")