from .part_detection_in_top import PartDetectionInTopModel
from ..colors import color_green, color_red

class HdlSidInClassificationModel:
    name = 'hdl_sid_in'
    imgsz = 64
    target_detections = {PartDetectionInTopModel.CLASS_HDL_SID_IN}

    ordered_class_list = [
        '83110M74L00-5PK',
        '83110M74L00-V6N',
        '83110M74L10-C48',
        '83110M74L10-GMN'
    ]

    class_names = {k: 'HDL_SID_IN' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}
