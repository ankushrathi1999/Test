from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class BoltOpenClassificationModel:
    name = 'bolt_open_classification'
    imgsz = 64
    target_detections = {PartDetectionInTopModel.CLASS_BOLT_OPEN}

    ordered_class_list = [
        'OK_bolt_open',
        'NG_bolt_open',
    ]

    class_names = {k: 'BOLT_OPEN' for k in ordered_class_list}
    class_names['NG_bolt_open'] = 'NG_BOLT_OPEN'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_bolt_open'] = color_red
