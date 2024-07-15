from collections import defaultdict
import logging

from .detection import DetectionResult
from config.colors import color_green, color_red
from config.models.bezel_switch_classification import BezelSwitchClassificationModel
from config.config import config, get_vehicle_parts_lookup

logger = logging.getLogger(__name__)

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')
BEZEL_SWITCH_IOU_THRESHOLD = api_config.getfloat('child_box_iou_threshold')
ALLOW_OK_TO_NG = api_config.getboolean('allow_ok_to_ng')
BEZEL_LABEL_OFFSET = 35

def aggregate_results(result_counts):
    result_counts = sorted(result_counts.items(), key=lambda x: x[1], reverse=True)
    ok_counts = [res for res in result_counts if res[0][1] == DetectionResult.OK]
    if len(ok_counts) > 0 and ok_counts[0][1] >= RESULT_COUNT_THRESHOLD:
        return ok_counts[0][0]
    elif len(result_counts) > 0 and result_counts[0][1] >= RESULT_COUNT_THRESHOLD:
        return result_counts[0][0]
    return None

def aggregate_list_results(result_counts):
    result_counts = sorted(result_counts.items(), key=lambda x: x[1], reverse=True)
    ok_counts = [res for res in result_counts if all([r[1] == DetectionResult.OK for r in res[0]])]
    if len(ok_counts) > 0 and ok_counts[0][1] >= RESULT_COUNT_THRESHOLD:
        return ok_counts[0][0]
    elif len(result_counts) > 0 and result_counts[0][1] >= RESULT_COUNT_THRESHOLD:
        return result_counts[0][0]
    return None

class BezelGroup:

    def __init__(self, vehicle_model):
        vehicle_parts_lookup = get_vehicle_parts_lookup()
        
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
        self.bezel_result = DetectionResult.MISSING # ok, incorrect_part
        self.bezel_pred = None # part number
        self.switch_results = [DetectionResult.MISSING for _ in self.switch_part_ids] # all types of errors
        self.switch_preds = [None for _ in self.switch_part_ids] # part number list

        logger.info('Init BezelGroup: inspection_enabled=%s has_bezel_master=%s has_switch_master=%s',
                     self.inspection_enabled, self.has_bezel_master, self.has_switch_master)
        logger.info('bezel_part_id=%s bezel_part_name=%s n_rows=%s',self.bezel_part_id, self.bezel_part_name, self.n_rows)
        logger.info('switch_part_ids=%s switch_part_names=%s switch_positions=%s', self.switch_part_ids, self.switch_part_names, self.switch_positions)

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
    
    def get_result_by_part_name(self, part_results, part_name):
        bezel_results = [p for p in part_results if p.get('type') == 'bezel']
        switch_results = [p for p in part_results if p.get('type') == 'bezel_switch']
        switch_pos_lookup = {res['position']:res for res in switch_results}
        if part_name.startswith('BZ_SW_'):
            try:
                position = int(part_name.replace('BZ_SW_', ''))
                part = switch_pos_lookup.get(position)
                return part['result'] if part is not None else None
            except ValueError:
                logger.warn("Failed to parse part_name: %s", part_name)
        elif part_name == 'BZ_AS_SW':
            return bezel_results[0]['result'] if len(bezel_results) > 0 else None
        return None

    def update(self, bezel_detections, switch_detections):
        if not self.inspection_enabled:
            return
        logger.debug("Updating bezel group")
        
        bezel_detection = max(bezel_detections, key=lambda detection: detection.confidence) if len(bezel_detections) > 0 else None
        switch_detections = [detection for detection in switch_detections if box_contains(bezel_detection.bbox, detection.bbox) >= BEZEL_SWITCH_IOU_THRESHOLD] if bezel_detection is not None else switch_detections

        # Inspection only happens when a contianer with the right number of switches is identified
        if bezel_detection is None or (len(switch_detections) != len(self.switch_part_ids)):
            logger.debug('bezel group condition not matched: %s',
                         (bezel_detection is None, len(switch_detections), len(self.switch_part_ids)))
            return
        
        # Bezel
        if self.has_bezel_master:
            pred_bezel_part = bezel_detection.classification_details.part_number
            result = DetectionResult.OK if pred_bezel_part == self.bezel_part_id else DetectionResult.INCORRECT_PART
            logger.debug("Current result: pred_bezel_part=%s result=%s", pred_bezel_part, result)
            # Keep in OK state if already passed
            if not ALLOW_OK_TO_NG and self.bezel_result == DetectionResult.OK:
                result = DetectionResult.OK
                pred_bezel_part = self.bezel_pred
                logger.debug("Updated result: pred_bezel_part=%s result=%s", pred_bezel_part, result)
            logger.debug("Counts: %s", self.bezel_results_count)
            self.bezel_results_count[(pred_bezel_part, result)] += 1
            bezel_detection.final_details.color = color_green if result == DetectionResult.OK else color_red
            bezel_detection.final_details.result = result
            bezel_detection.final_details.ignore = False
            result = aggregate_results(self.bezel_results_count)
            # if len(self.bezel_results_count) > 0:
            if result is not None:
                # result, result_count = sorted(self.bezel_results_count.items(), key=lambda x: x[1], reverse=True)[0]
                # if result_count >= RESULT_COUNT_THRESHOLD:
                self.bezel_pred = result[0]
                self.bezel_result = result[1]
                logger.debug("Bezel final result: bezel_pred=%s bezel_result=%s", self.bezel_pred, self.bezel_result)
            else:
                logger.debug("Bezel final result is not available yet.")
        else:
            logger.debug("Bezel master unavailable. Skipping bezel inspection.")
        
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
        logger.debug("Switch predictions. preds=%s results=%s", preds, results)

        # Keep in OK state if already passed
        if not ALLOW_OK_TO_NG and set(self.switch_results) == {DetectionResult.OK}:
            results = [DetectionResult.OK for _ in self.switch_part_ids]
            preds = self.switch_preds
            logger.debug("Updated switch predictions. preds=%s results=%s", preds, results)

        # Incorrect Position case: All parts match but order is incorrect
        if results != [DetectionResult.OK for _ in self.switch_part_ids]:
            logger.debug("Evaluating incorrect position case: preds=%s switch_part_ids=%s", set(preds), set(self.switch_part_ids))
            if set(preds) == set(self.switch_part_ids):
                logger.debug("Incorrect position case detected.")
                results = [DetectionResult.INCORRECT_POSITION if result == DetectionResult.INCORRECT_PART else result for result in results]

        # Compute label offsets
        row_top = [detection for detection in switch_detections if detection.extra_params['row_num'] == 1]
        for i, detection in enumerate(row_top):
            detection.final_details.label_position = 'top'
            detection.final_details.label_offset = (len(row_top)-i-1) * BEZEL_LABEL_OFFSET
        row_bottom = [detection for detection in switch_detections if detection.extra_params['row_num'] == 2]
        for i, detection in enumerate(row_bottom):
            detection.final_details.label_position = 'bottom'
            detection.final_details.label_offset = (len(row_bottom)-i-1) * BEZEL_LABEL_OFFSET

        # todo: part name should be looked up for actual part from a part number lookup for all detections
        for detection, result, part_name in zip(switch_detections, results, self.switch_part_names):
            if result in {DetectionResult.OK, DetectionResult.FLIP}:
                detection.final_details.label = part_name
            detection.final_details.color = color_green if result == DetectionResult.OK else color_red
            detection.final_details.result = result
        
        logger.debug("Switch result counts: %s", self.switch_results_counts)
        self.switch_results_counts[tuple(zip(preds, results))] += 1

        results = aggregate_list_results(self.switch_results_counts)
        if results is not None:
            # if len(self.switch_results_counts) > 0:
            # results, result_count = sorted(self.switch_results_counts.items(), key=lambda x: x[1], reverse=True)[0]
            # if result_count >= RESULT_COUNT_THRESHOLD:
            self.switch_preds = [res[0] for res in results]
            self.switch_results = [res[1] for res in results]
            logger.debug("Switch final result: switch_preds=%s switch_results=%s", self.switch_preds, self.switch_results)
        else:
            logger.debug("Switch final result is not available yet.")

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
    for i, row in enumerate(rows):
        for detection in row:
            detection.extra_params['row_num'] = i+1
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
