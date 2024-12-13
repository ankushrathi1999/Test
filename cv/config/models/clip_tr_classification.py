from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class ClipTrClassificationModel:
    name = 'clip_tr_classification'
    imgsz = 32
    target_detections = {PartDetectionInTopModel.CLASS_CLIP}

    ordered_class_list = [
        '09409M06314-5PK',
        '09409M06314-V6N',
        'NG_clip_tr',
    ]

    class_names = {k: 'CLIP' for k in ordered_class_list}
    class_names['NG_clip_tr'] = 'NG_CLIP_TR'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_clip_tr'] = color_red


