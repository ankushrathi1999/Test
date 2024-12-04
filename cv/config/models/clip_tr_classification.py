from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class ClipTrClassificationModel:
    name = 'clip_tr_classification'
    imgsz = 32
    target_detections = {PartDetectionInTopModel.CLASS_CLIP}

    ordered_class_list = [
        '09409M06314-5PK',
        '09409M06314-V6N',
    ]

    class_names = {k: 'CLIP' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}


# 09409M06314-5PK: 752
# 09409M06314-V6N: 763