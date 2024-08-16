from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

part_sw_lgt_yhbcx_basic_lookup = {
    'YHB': '37210M72R00',
    'YL1': '37210M74L00',
    'YXA': '37210M68P01',
}

class LightsWiperClassificationModel:
    name = 'lights_wiper_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_lgt_wip_left, PartDetectionModel.CLASS_lgt_wip_right}

    ordered_class_list = [
        '37210M72R10',
        '37210M72R50',
        '37210M74L40',
        '37210M74L60',
        '37210M79M00',
        'SW_WIP_YHBC_68P51_SW_WIP_YHBC_72R10', 
        'SW_WIP_YHBC_72R30_SW_WIP_YHBC_68P41', 
        '37310M74L20',
        'SW_WIP_YXA_01_SW_WIP_YHBC_72R00_SW_WIP_YL1_00',
        '37310M68P21',
        'sw_lgt_yhbcx_basic',
    ]

    # Note: The class names are currently being used to distnguish between lights and wiper
    class_names = {
        '37210M72R10': 'SW_LGT',
        '37210M72R50': 'SW_LGT',
        '37210M74L40': 'SW_LGT',
        '37210M74L60': 'SW_LGT',
        '37210M79M00': 'SW_LGT',
        'SW_WIP_YHBC_68P51_SW_WIP_YHBC_72R10': 'SW_WIP', 
        'SW_WIP_YHBC_72R30_SW_WIP_YHBC_68P41': 'SW_WIP', 
        '37310M74L20': 'SW_WIP',
        'SW_WIP_YXA_01_SW_WIP_YHBC_72R00_SW_WIP_YL1_00': 'SW_WIP',
        '37310M68P21': 'SW_WIP',
        'sw_lgt_yhbcx_basic': 'SW_LGT',
    }
    class_colors = {k: color_green for k in ordered_class_list}  

    @staticmethod
    def get_part_number(detection_label, class_name, vehicle_category, vehicle_type):
        if class_name == 'SW_WIP_YXA_01_SW_WIP_YHBC_72R00_SW_WIP_YL1_00':
            if vehicle_category == 'YL1':
                return '37310M74L00'
            else:
                return 'SW_WIP_YXA_01_SW_WIP_YHBC_72R00'
        elif class_name == 'sw_lgt_yhbcx_basic':
            return part_sw_lgt_yhbcx_basic_lookup.get(vehicle_category)
        else:
            return class_name
