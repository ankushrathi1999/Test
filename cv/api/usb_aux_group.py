from collections import defaultdict
import yaml

from .detection import DetectionResult
from config.colors import color_green, color_red

RESULT_COUNT_THRESHOLD = 2
IOU_THRESHOLD = 0.9

with open('./config/vehicle_parts_new.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

class UsbAuxGroup:

    def __init__(self, vehicle_model):
        # Load part details from vehicle_model
        self.part_ids = [] # List of part numbers
        self.part_names = [] # List of part names
        self.part_positions= [] # List of part positions
        self.inspection_enabled = vehicle_model in vehicle_parts_lookup

        if self.inspection_enabled:
            part_details = vehicle_parts_lookup[vehicle_model]['usb_aux_group']
            for i, detail in enumerate(part_details.get('parts', [])):
                self.part_ids.append(detail['part_number'])
                self.part_names.append(detail['part_name'])
                self.part_positions.append(i+1)

        self.has_master = len(self.part_ids) > 1

        # Predictions
        self.part_results_counts = defaultdict(int)

        # Selection
        self.part_results = [DetectionResult.NOT_EVALUATED for _ in self.part_ids] # all types of errors
        self.part_preds = [None for _ in self.part_ids] # part number list

    def get_part_results(self):
        parts = []
        if self.has_master:
            for part_id, part_name, part_position, part_pred, part_result in zip(
                self.part_ids, self.part_names, self.part_positions, self.part_preds, self.part_results):
                parts.append({
                    'part_id': part_id,
                    'part_name': part_name,
                    'result': part_result,
                    'part_pred': part_pred,
                    'position': part_position,
                    'type': 'usb_aux',
                })
        return parts

    # todo: need to implement
    # def get_ordered_part_results(self, part_results):
    #     switch_results = [p for p in part_results if p.get('type') == 'bezel_switch']
    #     switch_pos_lookup = {res['position']:res for res in switch_results}
    #     ordered_results = []
    #     for i in range(11): # Max 11 switches
    #         ordered_results.append(switch_pos_lookup.get(i+1))
    #     ordered_results.append(bezel_results[0] if len(bezel_results) > 0 else None)
    #     return ordered_results

    def update(self, container_detections, part_detections):
        if not self.inspection_enabled:
            return
        
        container_detection = max(container_detections, key=lambda detection: detection.confidence) if len(container_detections) > 0 else None
        part_detections = [detection for detection in part_detections if box_contains(container_detection.bbox, detection.bbox) >= IOU_THRESHOLD] if container_detection is not None else part_detections

        # Inspection only happens when a contianer with the right number of parts is identified
        if container_detection is None or (len(part_detections) != len(self.part_ids)):
            return
        
        part_detections = list(sorted(part_detections, key=lambda detection: detection.bbox[0]))
        preds = []
        results = []
        for detection, part_id in zip(part_detections, self.part_ids):
            detection.final_details.ignore = False
            pred_part = detection.classification_details.part_number
            if pred_part == part_id:
                result = DetectionResult.OK
            else:
                result = DetectionResult.INCORRECT_PART
            preds.append(pred_part)
            results.append(result)

        # Incorrect Position case: All parts match but order is incorrect
        if results != [DetectionResult.OK for _ in self.part_ids]:
            if set(preds) == set(self.part_ids):
                results = [DetectionResult.INCORRECT_POSITION if result == DetectionResult.INCORRECT_PART else result for result in results]

        # todo: part name should be looked up for actual part from a part number lookup for all detections
        for detection, result, part_name in zip(part_detections, results, self.part_names):
            if result in {DetectionResult.OK, DetectionResult.FLIP}:
                detection.final_details.label = part_name
            detection.final_details.color = color_green if result == DetectionResult.OK else color_red
            detection.final_details.result = result
        
        self.part_results_counts[tuple(zip(preds, results))] += 1

        if len(self.part_results_counts) > 0:
            results, result_count = sorted(self.part_results_counts.items(), key=lambda x: x[1], reverse=True)[0]
            if result_count >= RESULT_COUNT_THRESHOLD:
                self.part_preds = [res[0] for res in results]
                self.part_results = [res[1] for res in results]

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
