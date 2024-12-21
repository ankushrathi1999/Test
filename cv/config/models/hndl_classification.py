# from .part_detection_in_top import PartDetectionInTopModel
from .part_detection_out import PartDetectionOutModel
from ..colors import color_green, color_red

class HndlClassificationModel:
    name = 'hndl_classification'
    imgsz = 128
    target_detections = {PartDetectionOutModel.CLASS_HNDL}

    ordered_class_list = [
        'with_hole',
        'with_hole_switch',
        'with_switch',
        'without_hole',
    ]

    class_names = {k: 'HNDL' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}
