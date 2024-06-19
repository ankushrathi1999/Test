from collections import defaultdict
import yaml

from .detection import DetectionResult
from config.colors import color_green, color_red
from config.models.bezel_switch_classification import BezelSwitchClassificationModel
from config.config import config

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')
BEZEL_SWITCH_IOU_THRESHOLD = api_config.getfloat('child_box_iou_threshold')

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)
print("Vehicles Registered in YAML:", len(vehicle_parts_lookup))

class BezelGroup:

    def __init__(self, vehicle_model):
        # Load part details from vehicle_model
        self.bezel_part_id = None
        self.bezel_part_name = None
        self.switch_part_ids = [] # List of part numbers
        self.switch_part_names = [] # List of part names
        self.switch_positions= [] # List of part positions
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup and 'bezel' in vehicle_parts_lookup[vehicle_model]
        self.n_rows = 1

        if self.inspection_enabled:
            part_details = vehicle_parts_lookup[vehicle_model]['bezel']
            self.bezel_part_id = part_details['id']
            self.bezel_part_name = part_details['name']
            switches_top = part_details['switches_top']
            self.switch_part_ids = [s['id'] for s in switches_top]
            self.switch_part_names = [s['name'] for s in switches_top]
            self.switch_positions = [s['position'] for s in switches_top]
            if part_details['n_rows'] > 1:
                switches_bottom = part_details['switches_bottom']
                self.switch_part_ids.extend([s['id'] for s in switches_bottom])
                self.switch_part_names.extend([s['name'] for s in switches_bottom])
                self.switch_positions.extend([s['position'] for s in switches_bottom])
                self.n_rows = 2

        self.has_bezel_master = self.bezel_part_id not in {None, 'na'}
        self.has_switch_master = len(self.switch_part_ids) > 0 and self.switch_part_ids[0] != 'na'

        # Predictions
        self.bezel_results_count = defaultdict(int)
        self.switch_results_counts = defaultdict(int)

        # Selection
        self.bezel_result = DetectionResult.NOT_EVALUATED # ok, incorrect_part
        self.bezel_pred = None # part number
        self.switch_results = [DetectionResult.NOT_EVALUATED for _ in self.switch_part_ids] # all types of errors
        self.switch_preds = [None for _ in self.switch_part_ids] # part number list

    def get_part_results(self):
        parts = []
        self.has_bezel_master and parts.append({
            'part_id': self.bezel_part_id,
            'part_name': self.bezel_part_name,
            'result': self.bezel_result,
            'part_pred': self.bezel_pred,
            'type': 'bezel',
            'spec': self.bezel_part_id,
            'actual': self.bezel_pred,
            'key': 'BZ_AS_SW',
        })
        if self.has_switch_master:
            for part_id, part_name, part_position, part_pred, part_result in zip(
                self.switch_part_ids, self.switch_part_names, self.switch_positions, self.switch_preds, self.switch_results):
                parts.append({
                    'part_id': part_id,
                    'part_name': part_name,
                    'result': part_result,
                    'part_pred': part_pred,
                    'position': part_position,
                    'type': 'bezel_switch',
                    'spec': part_id,
                    'actual': part_pred,
                    'key': 'BZ_SW_{}'.format(part_position),
                })
        return parts

    def get_ordered_part_results(self, part_results):
        bezel_results = [p for p in part_results if p.get('type') == 'bezel']
        switch_results = [p for p in part_results if p.get('type') == 'bezel_switch']
        switch_pos_lookup = {res['position']:res for res in switch_results}
        ordered_results = []
        for i in range(11): # Max 11 switches
            ordered_results.append(switch_pos_lookup.get(i+1))
        ordered_results.append(bezel_results[0] if len(bezel_results) > 0 else None)
        return ordered_results

    def update(self, bezel_detections, switch_detections):
        if not self.inspection_enabled:
            return
        
        bezel_detection = max(bezel_detections, key=lambda detection: detection.confidence) if len(bezel_detections) > 0 else None
        switch_detections = [detection for detection in switch_detections if box_contains(bezel_detection.bbox, detection.bbox) >= BEZEL_SWITCH_IOU_THRESHOLD] if bezel_detection is not None else switch_detections

        # Inspection only happens when a contianer with the right number of switches is identified
        if bezel_detection is None or (len(switch_detections) != len(self.switch_part_ids)):
            # for detection in [*bezel_detections, *switch_detections]:
            #     detection.final_details.ignore = True
            return
        
        # Bezel
        if self.has_bezel_master:
            pred_bezel_part = bezel_detection.classification_details.part_number
            result = DetectionResult.OK if pred_bezel_part == self.bezel_part_id else DetectionResult.INCORRECT_PART
            self.bezel_results_count[(pred_bezel_part, result)] += 1
            bezel_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
            bezel_detection.final_details.result = result
            bezel_detection.final_details.ignore = False
            if len(self.bezel_results_count) > 0:
                result, result_count = sorted(self.bezel_results_count.items(), key=lambda x: x[1], reverse=True)[0]
                if result_count >= RESULT_COUNT_THRESHOLD:
                    self.bezel_pred = result[0]
                    self.bezel_result = result[1]
        
        # Switches
        switch_detections = sort_switches(switch_detections, self.n_rows)
        preds = []
        results = []
        for detection, part_id in zip(switch_detections, self.switch_part_ids):
            detection.final_details.ignore = False
            pred_switch_part = detection.classification_details.part_number
            is_flip = detection.classification_details.is_flip
            if pred_switch_part == part_id:
                if is_flip:
                    result = DetectionResult.FLIP
                else:
                    result = DetectionResult.OK
            elif pred_switch_part == BezelSwitchClassificationModel.CLASS_MISSING:
                result = DetectionResult.MISSING
            else:
                result = DetectionResult.INCORRECT_PART
            preds.append(pred_switch_part)
            results.append(result)

        # Incorrect Position case: All parts match but order is incorrect
        if results != [DetectionResult.OK for _ in self.switch_part_ids]:
            if set(preds) == set(self.switch_part_ids):
                results = [DetectionResult.INCORRECT_POSITION if result == DetectionResult.INCORRECT_PART else result for result in results]

        # todo: part name should be looked up for actual part from a part number lookup for all detections
        for detection, result, part_name in zip(switch_detections, results, self.switch_part_names):
            if result in {DetectionResult.OK, DetectionResult.FLIP}:
                detection.final_details.label = part_name
            detection.final_details.color = color_green if result == DetectionResult.OK else color_red
            detection.final_details.result = result
        
        self.switch_results_counts[tuple(zip(preds, results))] += 1

        if len(self.switch_results_counts) > 0:
            results, result_count = sorted(self.switch_results_counts.items(), key=lambda x: x[1], reverse=True)[0]
            if result_count >= RESULT_COUNT_THRESHOLD:
                self.switch_preds = [res[0] for res in results]
                self.switch_results = [res[1] for res in results]

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
