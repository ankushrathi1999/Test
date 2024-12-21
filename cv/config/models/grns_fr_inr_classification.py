from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class GrnsFrInrClassificationModel:
    name = 'grns_fr_inr_classification'
    imgsz = 128
    target_detections = {PartDetectionInTopModel.CLASS_GRNS_FR_INR}

    ordered_class_list = [
        '84750M66T00-5PK',
        '84750M72R00-5PK',
        '84750M72R10-5PK',
        '84750M79M00-5PK',
    ]

    class_names = {k: 'GRNS_FR_INR' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}
