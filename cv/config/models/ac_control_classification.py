from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

class ACControlClassificationModel:
    name = 'ac_control_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_ac_control}

    ordered_class_list = [
        'auto_beige_yhb',
        'auto_black_yhbc',
        'auto_black_yl1',
        'auto_black_yxa',
        'manual_beige_no_defogger_yhb',
        'manual_black_defogger_yhb',
        'manual_black_defogger_yl1',
        'manual_black_no_defogger_yhb',
    ]

    class_names = {k: 'CONT_HVAC' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}