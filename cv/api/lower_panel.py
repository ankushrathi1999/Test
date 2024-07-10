import yaml
from collections import defaultdict

from .detection import DetectionResult
from .classification_part import ClassificationPart
from config.models import ScrewDetectionModel
from config.config import config

api_config = config['api_common']
RESULT_COUNT_THRESHOLD = api_config.getint('result_count_threshold')
ALLOW_OK_TO_NG = api_config.getboolean('allow_ok_to_ng')

with open('./config/vehicle_parts.yaml') as x:
    vehicle_parts_lookup = yaml.safe_load(x)

class LowerPanel(ClassificationPart):
    def __init__(self, vehicle_model, detection_class, artifact):
        super().__init__(vehicle_model, detection_class, artifact)
        self.n_screws = vehicle_parts_lookup.get(vehicle_model, {}).get('n_screws', 0)
        self.screw_counts = defaultdict(int)

    def update(self, part_detections, detection_groups):
        if not self.inspection_enabled:
            return
        super().update(part_detections, detection_groups)
        print("Updating lower panel classification - screw inspection:", self.detection_class)
        
        screw_detections = [
            *detection_groups.get(ScrewDetectionModel.CLASS_SCREW_BIG, []),
            *detection_groups.get(ScrewDetectionModel.CLASS_SCREW_SMALL, []),
        ]
        for detection in screw_detections:
            self.screw_counts[detection.tracking_id] += 1
            detection.final_details.ignore = False

        if self.part_result == DetectionResult.OK:
            all_screw_detections = [tracking_id for tracking_id, count in self.screw_counts.items() if count >= RESULT_COUNT_THRESHOLD]
            print("Evaluating screw counts:", len(all_screw_detections), self.n_screws)
            if len(all_screw_detections) < self.n_screws:
                self.part_result = DetectionResult.MISSING_SCREWS

