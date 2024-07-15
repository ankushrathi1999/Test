import yaml
import json
import logging

from .detection import DetectionResult
from .classification_part import ClassificationPart
from config.colors import color_green, color_red
from config.config import config

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

class SteeringCover(ClassificationPart):
    def update(self, part_detections, detection_groups):
        if not self.inspection_enabled:
            return
        logger.debug("Updating steering cover classification: %s", self.detection_class)
        
        # key_detections = detection_groups.get(PartDetectionModel.CLASS_key, [])
        # key_detection = max(key_detections, key=lambda detection: detection.confidence) if len(key_detections) > 0 else None

        part_detection = max(part_detections, key=lambda detection: detection.confidence) if len(part_detections) > 0 else None
        if part_detection is None:
            return
        
        img_height, img_width = self.artifact.data.frames[1].shape[:2]
        x2_pos = part_detection.bbox[2] / img_width
        # x2_check_start, x2_check_end = [0.45, 0.8] if self.artifact.vehicle_type == "RHD" else [0.1, 0.45]
        x2_check_start, x2_check_end = [0, 0.56]
        if x2_pos < x2_check_start or x2_pos> x2_check_end:
            logger.debug('Steering skip: %s', [x2_pos, x2_check_start, x2_check_end, part_detection.bbox, img_width, img_height])
            return
        
        # is_key_present = key_detection is not None and box_contains(part_detection.bbox, key_detection.bbox) > 0.3
        # print("Key detection:", is_key_present, key_detection is None)
        # if key_detection is not None:
        #     print("box contains:", box_contains(part_detection.bbox, key_detection.bbox))
                
        # pred_part_group = part_detection.classification_details.part_number
        #PartClassificationModel.get_part_number_steering_cover(pred_part_group, is_key_present, self.artifact.vehicle_category)
        pred_part = part_detection.classification_details.part_number
        result = DetectionResult.OK if pred_part == self.part_id else DetectionResult.INCORRECT_PART
        logger.debug("Current result: pred_part=%s result=%s part_id=%s missing_class_name=%s is_miss_inspection=%s",
              pred_part, result, self.part_id, self.missing_class_name, self.is_miss_inspection)
        # Keep in OK state if already passed
        if not ALLOW_OK_TO_NG and self.part_result == DetectionResult.OK:
            result = DetectionResult.OK
            pred_part = self.part_pred
            logger.debug("Updated result: pred_part=%s result=%s", pred_part, result)
        self.part_results_count[(pred_part, result)] += 1
        part_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
        part_detection.final_details.result = result
        part_detection.final_details.ignore = False
        if len(self.part_results_count) > 0:
            # result, result_count = sorted(self.part_results_count.items(), key=lambda x: x[1], reverse=True)[0]
            result = aggregate_results(self.part_results_count)
            # if result_count >= RESULT_COUNT_THRESHOLD:
            if result is not None:
                self.part_pred = result[0]
                self.part_result = result[1]
                logger.debug("Final result: part_pre=%s part_result=%s", self.part_pred, self.part_result)
            else:
                logger.debug("Result is not available yet.")

def box_contains(box1, box2): #parent, child
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2

    # Intersection rectangle
    ix1 = max(x1, x3)
    iy1 = max(y1, y3)
    ix2 = min(x2, x4)
    iy2 = min(y2, y4)

    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    intersection_area = (ix2 - ix1) * (iy2 - iy1)

    # Calculate each box area
    box2_area = (x4 - x3) * (y4 - y3)

    return intersection_area / box2_area