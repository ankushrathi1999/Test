from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

part_number_lookup = {
    ('YHB', 'orn_ctr', 'or_ip_yhbc_black', 'RHD'): '73081M73R00-5PK',
    ('YHB', 'orn_ctr', 'or_ip_yhbc_black', 'LHD'): '73081M73R50-5PK',
    ('YHB', 'orn_ctr', 'or_ip_yhbc_brown', 'RHD'): '73081M73R00-R8R',
    ('YHB', 'orn_ctr', 'or_ip_yhbc_teak', 'RHD'): '73081M72R10-QWD',
    ('YHB', 'orn_ctr', 'or_ip_yhbc_teak', 'LHD'): '73081M72R60-QWD',    
    ('YHC', 'orn_ctr', 'or_ip_yhbc_dual_silver', 'RHD'): '73068M72S00-DUF',
    ('YL1', 'orn_ctr', 'or_ip_yl1_silver', 'LHD'): '73852M79M10-PPL',
    ('YL1', 'orn_ctr', 'or_ip_yl1_silver', 'RHD'): '73852M79M20-PPL',
    ('YL1', 'orn_ctr', 'or_ip_yl1_silver_smoke', 'RHD'): '73870M82R00-DE4',
    ('YL1', 'orn_ctr', 'or_ip_yl1_silver_smoke', 'LHD'): '73870M82R10-DE4',
    ('YL1', 'orn_ctr', 'or_ip_yl1_wood', 'LHD'): '73852M79M10-QM1',
    ('YL1', 'orn_ctr', 'or_ip_yl1_wood', 'RHD'): '73852M79M20-QM1',
    ('YL1', 'orn_ctr', 'or_ip_yl1_wood_smoke', 'RHD'): '73870M82R00-DE3',
    ('YL1', 'orn_ctr', 'or_ip_yl1_wood_smoke', 'LHD'): '73870M82R10-DE3',
    ('YHB', 'orn_drvr', 'or_ip_yhbc_black', 'RHD'): '73832M73R00-5PK',
    ('YHB', 'orn_drvr', 'or_ip_yhbc_black', 'LHD'): '73832M73R50-5PK',
    ('YHB', 'orn_drvr', 'or_ip_yhbc_brown', 'RHD'): '73832M73R00-R8R',
    ('YHB', 'orn_drvr', 'or_ip_yhbc_teak', 'RHD'): '73832M72R10-QWD',
    ('YHB', 'orn_drvr', 'or_ip_yhbc_teak', 'LHD'): '73832M72R60-QWD',    
    ('YHC', 'orn_drvr', 'or_ip_yhbc_dual_silver', 'RHD'): '73081M72S00-DUF',
    ('YL1', 'orn_drvr', 'or_ip_yl1_silver', 'LHD'): '73851M79M10-PPL',
    ('YL1', 'orn_drvr', 'or_ip_yl1_silver', 'RHD'): '73851M79M00-PPL',
    ('YL1', 'orn_drvr', 'or_ip_yl1_silver_smoke', 'RHD'): '73851M79M00-PPL',
    ('YL1', 'orn_drvr', 'or_ip_yl1_silver_smoke', 'LHD'): '73860M82R10-DE4',
    ('YL1', 'orn_drvr', 'or_ip_yl1_wood', 'LHD'): '73851M79M10-QM1',
    ('YL1', 'orn_drvr', 'or_ip_yl1_wood', 'RHD'): '73851M79M00-QM1',
    ('YL1', 'orn_drvr', 'or_ip_yl1_wood_smoke', 'RHD'): '73860M82R00-DE3',
    ('YL1', 'orn_drvr', 'or_ip_yl1_wood_smoke', 'LHD'): '73860M82R10-DE3',
}

class OrnClassificationModel:
    name = 'orn_classification'
    imgsz = 256
    target_detections = {PartDetectionModel.CLASS_orn_ctr, PartDetectionModel.CLASS_orn_drvr}

    ordered_class_list = [
        'or_ip_yhbc_black',
        'or_ip_yhbc_brown',
        'or_ip_yhbc_dual_silver',
        'or_ip_yhbc_teak',
        'or_ip_yl1_silver',
        'or_ip_yl1_wood',
        'or_ip_yl1_wood_smoke',
    ]

    class_names = {k: 'ORN' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}

    @staticmethod
    def get_part_number(detection_label, class_name, vehicle_category, vehicle_type):
        return part_number_lookup.get((vehicle_category, detection_label, class_name, vehicle_type))