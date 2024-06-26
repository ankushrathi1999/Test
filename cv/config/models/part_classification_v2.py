from .part_detection_v2 import PartDetectionModel
from ..colors import color_white, color_green

part_upper_panel_lookup = {
    ('YHB', 'LHD', 'ip_upr_black'): '73111M72R50-5PK',
    ('YHB', 'RHD', 'ip_upr_black'): '73111M72R00-5PK',
    ('YHB', 'RHD', 'ip_upr_brown'): '73111M72R00-R8R',
    ('YHC', 'RHD', 'ip_upr_black'): '73111M72R00-5PK',
    ('YL1', 'LHD', 'ip_upr_black'): '73111M79M12-5PK',
    ('YL1', 'RHD', 'ip_upr_black'): '73111M79M02-5PK',
    ('YXA', 'RHD', 'ip_upr_black'): '73111M66T00-5PK'
}

part_lvr_vt_yl1_lookup = {
    ('ac_left', 'lvr_vt_black'): '73640M79M00-C48',
    ('ac_left', 'lvr_vt_chrome'): '73640M79M00-BJC',
    ('ac_right', 'lvr_vt_black'): '73630M79M00-C48',
    ('ac_right', 'lvr_vt_chrome'): '73630M79M00-BJC'
}

part_garnish_yxa_lookup = {
    ('ac_garnish_yxa', 'gar_yxa_dvv'): '73084M66T10-DVV',
    ('ac_garnish_yxa', 'gar_yxa_eve'): '73084M66T10-EVE',
    ('ac_right', 'gar_yxa_dvv'): '73083M66T10-DVV',
    ('ac_right', 'gar_yxa_eve'): '73083M66T10-EVE'
}

part_garnish_yhbc_lookup = {
    ('LHD', 'ac_left'): '73086M72R10-C48',
    ('LHD', 'ac_right'): '73083M72R10-C48',
    ('RHD', 'ac_left'): '73086M72R00-C48',
    ('RHD', 'ac_right'): '73083M72R00-C48'
 }

# todo: combine lookup for yhb and yhcx after adding telescopic steering class
part_steering_cover_lookup_yhb = {
    ('clmn_cvr_black', True): '48400M55R00-5PK', # classification label x is_key_present
    ('clmn_cvr_black', False): '48400M55R10-5PK',
    # ('clmn_cvr_black', False): '48400M55T30-5PK',
    ('clmn_cvr_gray', True): '48400M55R00-R8R',
    ('clmn_cvr_gray', False): '48400M55R10-R8R',
}

part_steering_cover_lookup_yhcx = {
    ('clmn_cvr_black', True): '48400M55R00-5PK', # classification label x is_key_present
    # ('clmn_cvr_black', False): '48400M55R10-5PK',
    ('clmn_cvr_black', False): '48400M55T30-5PK',
    ('clmn_cvr_gray', True): '48400M55R00-R8R',
    ('clmn_cvr_gray', False): '48400M55R10-R8R',
}

part_steering_cover_lookup_yl1 = {
    ('clmn_cvr_black', True): '48400M74L00-5PK', # classification label x is_key_present
    ('clmn_cvr_black', False): '48400M79M30-5PK',
}

class PartClassificationModel:
    name = 'part_classification_v2'
    imgsz = 256
    target_detections = set([
        # PartDetectionModel.CLASS_ac_control, # Classifier
        # PartDetectionModel.CLASS_ac_ctr, # Detection
        # PartDetectionModel.CLASS_ac_ctr_left, # Detection
        # PartDetectionModel.CLASS_ac_ctr_right, # Detection
        PartDetectionModel.CLASS_ac_garnish_yxa,
        PartDetectionModel.CLASS_ac_left,
        PartDetectionModel.CLASS_ac_right,
        # PartDetectionModel.CLASS_cover_upper_yxa, # Detection
        PartDetectionModel.CLASS_garnish_drvr_inside_yl,
        # PartDetectionModel.CLASS_hazard_switches, # Detection
        # PartDetectionModel.CLASS_label_ac, # Detection only
        # PartDetectionModel.CLASS_lgt_wip_right, # Classifier
        # PartDetectionModel.CLASS_lower_panel, # Classifier
        # PartDetectionModel.CLASS_nozzle_left, # Detection
        # PartDetectionModel.CLASS_nozzle_right, # Detection
        # PartDetectionModel.CLASS_orn_ctr, # Classifier
        # PartDetectionModel.CLASS_orn_drvr, # Classifier
        # PartDetectionModel.CLASS_sensor_left, # Classifier
        # PartDetectionModel.CLASS_sensor_right, # Classifier
        PartDetectionModel.CLASS_steering_coil,
        PartDetectionModel.CLASS_steering_cover,
        # PartDetectionModel.CLASS_switch, # Detection
        PartDetectionModel.CLASS_upper_panel,
        # PartDetectionModel.CLASS_usb_aux, # Classifier
        # PartDetectionModel.CLASS_usb_aux_container, 
        # PartDetectionModel.CLASS_lgt_wip_left, # Classifier
    ])

    ordered_class_list = [
        '73824M73R50-5PK', # CVR_DRVR
        '73824M73R60-5PK',
        '73832M79M00-5PK',
        '73832M79M00-V6N',
        '73832M79M10-V6N',
        '73832M79M30-V6N',
        'clmn_cvr_black',
        'clmn_cvr_gray',
        'blue_lock',
        'white_lock',
        'yellow_lock',
        'gar_yxa_dvv',
        'gar_yxa_eve',
        'ip_upr_black',
        'ip_upr_brown',
        'lvr_vt_black',
        'lvr_vt_chrome',
 ]

    class_names = {
        '73824M73R50-5PK': 'CVR_DRVR',
        '73824M73R60-5PK': 'CVR_DRVR',
        '73832M79M00-5PK': 'CVR_DRVR',
        '73832M79M00-V6N': 'CVR_DRVR',
        '73832M79M10-V6N': 'CVR_DRVR',
        '73832M79M30-V6N': 'CVR_DRVR',
        'clmn_cvr_black': 'CLMN_CVR',
        'clmn_cvr_gray': 'CLMN_CVR',
        'blue_lock': 'CT_COIL',
        'white_lock': 'CT_COIL',
        'yellow_lock': 'CT_COIL',
        'gar_yxa_dvv': 'GAR_YXA',
        'gar_yxa_eve': 'GAR_YXA',
        'ip_upr_black': 'IP_UPR',
        'ip_upr_brown': 'IP_UPR',
        'lvr_vt_black': 'LVR_VT',
        'lvr_vt_chrome': 'LVR_VT',
    }

    class_colors = {k: color_green for k in class_names.keys()}

    @staticmethod
    def get_part_number(detection_label_full, class_name, vehicle_category, vehicle_type):
        detection_label = detection_label_full.replace('part_detection_v2_', '')
        if detection_label_full in {PartDetectionModel.CLASS_upper_panel}:
            return part_upper_panel_lookup.get((vehicle_category, vehicle_type, class_name))
        elif vehicle_category == 'YL1' and detection_label_full in {PartDetectionModel.CLASS_ac_left, PartDetectionModel.CLASS_ac_right}:
            return part_lvr_vt_yl1_lookup.get((detection_label, class_name))
        elif vehicle_category == 'YXA' and detection_label_full in {PartDetectionModel.CLASS_ac_garnish_yxa, PartDetectionModel.CLASS_ac_right}:
            return part_garnish_yxa_lookup.get((detection_label, class_name))
        elif vehicle_category in {'YHB', 'YHC'} and detection_label_full in {PartDetectionModel.CLASS_ac_left, PartDetectionModel.CLASS_ac_right}:
            return part_garnish_yhbc_lookup.get((vehicle_type, detection_label))
        else:
            return class_name
        
    @staticmethod
    def get_part_number_steering_cover(class_name, is_key_present, vehicle_category):
        if vehicle_category == 'YHB':
            return part_steering_cover_lookup_yhb.get((class_name, is_key_present))
        elif vehicle_category in {'YHC', 'YXA'}:
            return part_steering_cover_lookup_yhcx.get((class_name, is_key_present))
        elif vehicle_category == 'YL1':
            return part_steering_cover_lookup_yl1.get((class_name, is_key_present))

