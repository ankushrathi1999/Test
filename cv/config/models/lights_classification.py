from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

part_sw_lgt_yhbcx_basic_lookup = {
    'YHB': '37210M72R00',
    'YL1': '37210M74L00',
    'YXA': '37210M68P01',
}

class LightsClassificationModel:
    name = 'lights_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_lights}

    ordered_class_list = [
        '37210M72R10',
        '37210M72R50',
        '37210M74L40',
        '37210M74L60',
        '37210M79M00',
        'sw_lgt_yhbcx_basic',
    ]

    class_names = {k: 'SW_LGT' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}  

    @staticmethod
    def get_part_number(detection_label, class_name, vehicle_category, vehicle_type):
        if class_name == 'sw_lgt_yhbcx_basic':
            return part_sw_lgt_yhbcx_basic_lookup.get(vehicle_category)
        else:
            return class_name