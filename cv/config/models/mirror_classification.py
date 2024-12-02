from .part_detection_out import PartDetectionOutModel
from ..colors import color_green, color_red

class MirrorClassificationModel:
    name = 'mirror_classification'
    imgsz = 64
    target_detections = {PartDetectionInTopModel.CLASS_MIRROR}

    ordered_class_list = [
        'with_light_YH',
        'with_light_YL1',
        'with_light_YXA',
        'without_light_YH',
    ]

    class_names = {k: 'MIRROR' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}
