from .part_detection_out import PartDetectionOutModel
from ..colors import color_green, color_red

class WthrOutClassificationModel:
    name = 'wthr_out_classification'
    imgsz = 32
    target_detections = {PartDetectionOutModel.CLASS_WTHR_OUT}

    ordered_class_list = [
        'OK_wthr_out',
        'NG_wthr_out',
    ]

    class_names = {k: 'WTHR_OUT' for k in ordered_class_list}
    class_names['NG_wthr_out'] = 'NG_WTHR_OUT'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_wthr_out'] = color_red
