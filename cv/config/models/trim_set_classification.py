from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class TrimSetClassificationModel:
    name = 'trim_set_classification'
    imgsz = 256
    target_detections = {PartDetectionInTopModel.CLASS_TRIM_SET}

    ordered_class_list = [
        '83071M72RA1-5PK',
        '83071M72R62-EQJ',
        '83071M51U03-DUG',
        'YH_brown_0',
        '83071M72R93-ERK',
        '83079M79M23-A6V',
        'YL1_brown',
        'YXA_black',
        '83071M66T20-ERT',
    ]

    class_names = {k: 'TRIM_SET' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}
