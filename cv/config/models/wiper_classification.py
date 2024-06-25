from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

class WiperClassificationModel:
    name = 'wiper_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_wiper}

    ordered_class_list = [
        'SW_WIP_YHBC_68P51_SW_WIP_YHBC_72R10', 
        'SW_WIP_YHBC_72R30_SW_WIP_YHBC_68P41', 
        '37310M74L20',
        'SW_WIP_YXA_01_SW_WIP_YHBC_72R00_SW_WIP_YL1_00',
        '37310M68P21',
    ]

    class_names = {k: 'SW_WIP' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}  

    @staticmethod
    def get_part_number(detection_label, class_name, vehicle_category, vehicle_type):
        if class_name == 'SW_WIP_YXA_01_SW_WIP_YHBC_72R00_SW_WIP_YL1_00':
            if vehicle_category == 'YL1':
                return '37310M74L00'
            else:
                return 'SW_WIP_YXA_01_SW_WIP_YHBC_72R00'
        else:
            return class_name