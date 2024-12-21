from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class StopOpenClassificationModel:
    name = 'stop_open_classification'
    imgsz = 128
    target_detections = {PartDetectionInTopModel.CLASS_STOP_OPEN}

    ordered_class_list = [
        '81810M80T00',
        '81830M63RB3',
        '81830M75L01',
    ]

    class_names = {k: 'STOP_OPEN' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}


# 81810M80T00: 514
# 81830M63RB3: 517
# 81830M75L01: 104