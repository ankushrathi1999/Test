from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class CapBzlClassificationModel:
    name = 'cap_bzl_classification'
    imgsz = 32
    target_detections = {PartDetectionInTopModel.CLASS_CAP_BZL}

    ordered_class_list = [
        '83755M74L00-5PK',
        '83755M74L00-V6N',
        'NG_cap_bzl',
    ]

    class_names = {k: 'CAP_BZL' for k in ordered_class_list}
    class_names['NG_cap_bzl'] = 'NG_CAP_BZL'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_cap_bzl'] = color_red
