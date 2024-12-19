from .part_detection_in_bottom import PartDetectionInBottomModel
from ..colors import color_green, color_red

class WthrFrOutClassificationModel:
    name = 'wthr_fr_open_classification'
    imgsz = 32
    target_detections = {PartDetectionInBottomModel.CLASS_WTHR_FR_OPEN}

    ordered_class_list = [
        'NG_wthr_fr_open',
        'OK_wthr_fr_open',
    ]

    class_names = {k: 'WTHR_FR_OPEN' for k in ordered_class_list}
    class_names['NG_wthr_fr_open'] = 'NG_WTHR_FR_OPEN'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_wthr_fr_open'] = color_red
