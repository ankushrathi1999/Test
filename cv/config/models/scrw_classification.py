from .part_detection_in_bottom import PartDetectionInBottomModel
from ..colors import color_green, color_red

class ScrwClassificationModel:
    name = 'scrw_classification'
    imgsz = 64
    target_detections = {PartDetectionInBottomModel.CLASS_SCRW}

    ordered_class_list = [
        'OK_scrw',
        'NG_scrw',
    ]

    class_names = {k: 'SCRW' for k in ordered_class_list}
    class_names['NG_scrw'] = 'NG_SCRW'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_scrw'] = color_red
