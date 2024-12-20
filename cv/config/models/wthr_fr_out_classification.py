from .part_detection_out import PartDetectionOutModel
from ..colors import color_green, color_red

class WthrOutClassificationModel:
    name = 'wthr_fr_out_classification'
    imgsz = 32
    target_detections = {PartDetectionOutModel.CLASS_WTHR_FR_OUT}

    ordered_class_list = [
        'NG_wthr_fr_out',
        'OK_wthr_fr_out',
    ]

    class_names = {k: 'WTHR_FR_OUT' for k in ordered_class_list}
    class_names['NG_wthr_fr_out'] = 'NG_WTHR_FR_OUT'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_wthr_fr_out'] = color_red
