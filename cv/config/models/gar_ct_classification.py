from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green


class GarCTClassificationModel:
    name = 'gar_ct_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_screen}

    ordered_class_list = [
        '73821M66T00-0CE',  # YXA14
        '73821M66T00-ZCA', # YXA24
    ]

    class_names = {k: 'GAR_IP_CT' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}