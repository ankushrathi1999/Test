from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

part_number_lookup = {
    ('YHB', 'LHD', 'ip_lwr_black'): '73121M72R50-5PK',
    ('YHB', 'RHD', 'ip_lwr_beige'): '73121M72R00-V6N',
    ('YHB', 'RHD', 'ip_lwr_black'): '73121M51U00-5PK',
    ('YHC', 'RHD', 'ip_lwr_black'): '73121M51U00-5PK',
    ('YL1', 'LHD', 'ip_lwr_beige'): '73121M79M10-V6N',
    ('YL1', 'LHD', 'ip_lwr_black'): '73121M79M10-5PK',
    ('YL1', 'RHD', 'ip_lwr_beige'): '73121M79M00-V6N',
    ('YL1', 'RHD', 'ip_lwr_black'): '73121M79M00-5PK',
    ('YXA', 'RHD', 'ip_lwr_black'): '73121M66T00-5PK',
}

class LowerPanelClassificationModel:
    name = 'lower_panel_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_lower_panel}

    ordered_class_list = [
        'ip_lwr_beige',
        'ip_lwr_black',
    ]

    class_names = {k: 'IP_LWR' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}  

    @staticmethod
    def get_part_number(detection_label, class_name, vehicle_category, vehicle_type):
        return part_number_lookup.get((vehicle_category, vehicle_type, class_name))