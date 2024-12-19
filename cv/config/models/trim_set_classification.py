from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class TrimSetClassificationModel:
    name = 'trim_set_classification'
    imgsz = 256
    target_detections = {PartDetectionInTopModel.CLASS_TRIM_SET}

    ordered_class_list = [
        'YH_black_0',
        'YH_black_1',
        'YH_black_2',
        'YH_brown_0',
        'YH_brown_1',
        'YL1_black',
        'YL1_brown',
        'YXA_black',
        'YXA_brown',
    ]

    class_names = {k: 'TRIM_SET' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}