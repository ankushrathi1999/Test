from collections import defaultdict
import yaml

from .detection import DetectionResult
from config.colors import color_green, color_red
from config.models.bezel_switch_classification import BezelSwitchClassificationModel

RESULT_COUNT_THRESHOLD = 2
BEZEL_SWITCH_IOU_THRESHOLD = 0.9

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)
print("Vehicles Registered in YAML:", len(vehicle_parts_lookup))

class BezelGroup:

    def __init__(self, vehicle_model):
        # Load part details from vehicle_model
        self.bezel_part_id = None
        self.bezel_part_name = None
        self.switch_part_types = [] # List of part types
        self.switch_part_ids = [] # List of part numbers
        self.switch_part_names = [] # List of part names
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup
        self.n_rows = 1

        if self.inspection_enabled:
            part_details = vehicle_parts_lookup[vehicle_model]['bezel']
            self.bezel_part_id = part_details['id']
            self.bezel_part_name = part_details['name']
            switches_top = part_details['switches_top']
            self.switch_part_ids = [s['id'] for s in switches_top]
            self.switch_part_names = [s['name'] for s in switches_top]
            self.switch_part_types = [s['type'] for s in switches_top]
            if part_details['n_rows'] > 1:
                switches_bottom = part_details['switches_bottom']
                self.switch_part_ids.extend([s['id'] for s in switches_bottom])
                self.switch_part_names.extend([s['name'] for s in switches_bottom])
                self.switch_part_types.extend([s['type'] for s in switches_bottom])
                self.n_rows = 2

        # Predictions
        self.bezel_results_count = defaultdict(int)
        self.switch_results_counts = defaultdict(int)

        # Selection
        self.bezel_result = DetectionResult.NOT_EVALUATED # ok, incorrect_part
        self.switch_results = [DetectionResult.NOT_EVALUATED for _ in self.switch_part_types] # all types of errors

    def update(self, bezel_detections, switch_detections):
        print('inspection_enabled:', self.inspection_enabled, len(bezel_detections))
        if not self.inspection_enabled:
            return
        if len(bezel_detections) == 0:
            return
        bezel_detection = max(bezel_detections, key=lambda detection: detection.confidence)
        print('bezel', bezel_detection.to_dict())
        for detection in bezel_detections:
            if detection is not bezel_detection:
                detection.final_details.ignore = True
        
        # Bezel
        pred_bezel_part = bezel_detection.classification_details.class_id
        result = DetectionResult.OK if pred_bezel_part == self.bezel_part_id else DetectionResult.INCORRECT_PART
        self.bezel_results_count[result] += 1
        bezel_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
        bezel_detection.final_details.result = result
        if len(self.bezel_results_count) > 0:
            result, result_count = sorted(self.bezel_results_count.items(), key=lambda x: x[1], reverse=True)[0]
            if result_count >= RESULT_COUNT_THRESHOLD:
                self.bezel_result = result
        
        # Switches
        switch_detections = [detection for detection in switch_detections if box_contains(bezel_detection.bbox, detection.bbox) >= BEZEL_SWITCH_IOU_THRESHOLD]
        if len(switch_detections) == len(self.switch_part_types):
            switch_detections = sort_switches(switch_detections, self.n_rows)
            preds = []
            results = []
            for detection, part_type in zip(switch_detections, self.switch_part_types):
                pred_switch_part = detection.classification_details.class_id
                if pred_switch_part == part_type:
                    result = DetectionResult.OK
                elif pred_switch_part == part_type + '_flip':
                    result = DetectionResult.FLIP
                elif pred_switch_part == BezelSwitchClassificationModel.CLASS_MISSING:
                    result = DetectionResult.MISSING
                else:
                    result = DetectionResult.INCORRECT_PART
                preds.append(pred_switch_part)
                results.append(result)

            # Incorrect Position case: All parts match but order is incorrect
            if results != [DetectionResult.OK for _ in self.switch_part_types]:
                if set(preds) == set(self.switch_part_types):
                    results = [DetectionResult.INCORRECT_POSITION if result == DetectionResult.INCORRECT_PART else result for result in results]

            for detection, result, part_name in zip(switch_detections, results, self.switch_part_names):
                if result in {DetectionResult.OK, DetectionResult.FLIP}:
                    detection.final_details.label = part_name
                detection.final_details.color = color_green if result == DetectionResult.OK else color_red
                detection.final_details.result = result
            
            self.switch_results_counts[tuple(results)] += 1

            if len(self.switch_results_counts) > 0:
                results, result_count = sorted(self.switch_results_counts.items(), key=lambda x: x[1], reverse=True)[0]
                if result_count >= RESULT_COUNT_THRESHOLD:
                    self.switch_results = results

def sort_switches(switch_detections, n_rows):
    if n_rows > 1:
        y_mean = sum([detection.bbox[1] for detection in switch_detections]) / len(switch_detections)
        rows = [[], []]
        for detection in switch_detections:
            if detection.bbox[1] < y_mean:
                rows[0].append(detection)
            else:
                rows[1].append(detection)
    else:
        rows = [switch_detections]
    rows = [sorted(row, key=lambda detection: detection.bbox[0]) for row in rows]
    return [detection for row in rows for detection in row]

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
