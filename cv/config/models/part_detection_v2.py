from ..colors import color_white, color_green

class PartDetectionModel:
    name = 'part_detection_v2'
    imgsz = 640
    target_cams = {'top', 'bottom', 'up'}
    tracking = False

    CLASS_ac_control = name + '_ac_control'
    CLASS_ac_ctr = name + '_ac_ctr'
    CLASS_ac_ctr_left = name + '_ac_ctr_left'
    CLASS_ac_ctr_right = name + '_ac_ctr_right'
    CLASS_ac_garnish_yxa = name + '_ac_garnish_yxa'
    CLASS_ac_left = name + '_ac_left'
    CLASS_ac_right = name + '_ac_right'
    CLASS_cover_upper_yxa = name + '_cover_upper_yxa'
    CLASS_dashboard = name + '_dashboard'
    CLASS_garnish_drvr_inside_yl = name + '_garnish_drvr_inside_yl'
    CLASS_hazard_switches = name + '_hazard_switches'
    CLASS_key = name + '_key'
    CLASS_label_ac = name + '_label_ac'
    CLASS_lgt_wip_right = name + '_lgt_wip_right'
    CLASS_lower_panel = name + '_lower_panel'
    CLASS_nozzle_left = name + '_nozzle_left' 
    CLASS_nozzle_right = name + '_nozzle_right' 
    CLASS_orn_ctr = name + '_orn_ctr'
    CLASS_orn_drvr = name + '_orn_drvr'
    CLASS_push_button = name + '_push_button'
    CLASS_screen = name + '_gar_ip_ctr'
    CLASS_sensor_left = name + '_sensor_left'
    CLASS_sensor_right = name + '_sensor_right'
    CLASS_speedometer = name + '_speedometer'
    CLASS_steering_coil = name + '_steering_coil'
    CLASS_steering_cover = name + '_steering_cover'
    CLASS_switch = name + '_switch'
    CLASS_upper_panel = name + '_upper_panel'
    CLASS_usb_aux = name + '_usb_aux'
    CLASS_usb_aux_container = name + '_usb_aux_container'
    CLASS_lgt_wip_left = name + '_lgt_wip_left'
    # Inferred Classes
    CLASS_lights = name + '_lights'
    CLASS_wiper = name + '_wiper'

    ordered_class_list = [
        CLASS_ac_control,
        CLASS_ac_ctr,
        CLASS_ac_ctr_left,
        CLASS_ac_ctr_right,
        CLASS_ac_garnish_yxa,
        CLASS_ac_left,
        CLASS_ac_right,
        CLASS_cover_upper_yxa,
        None, # dashboard
        CLASS_garnish_drvr_inside_yl,
        CLASS_hazard_switches,
        CLASS_key, # Not part of primary spec,
        CLASS_label_ac,
        CLASS_lgt_wip_right,
        CLASS_lower_panel,
        CLASS_nozzle_left,
        CLASS_nozzle_right,
        CLASS_orn_ctr,
        CLASS_orn_drvr,
        None, # CLASS_push_button,
        CLASS_screen,
        CLASS_sensor_left,
        CLASS_sensor_right,
        None, # CLASS_speedometer,
        CLASS_steering_coil,
        CLASS_steering_cover,
        CLASS_switch,
        CLASS_upper_panel,
        CLASS_usb_aux,
        CLASS_usb_aux_container,
        CLASS_lgt_wip_left,
    ]

    class_names = {
        CLASS_ac_control: 'ac_control',
        CLASS_ac_ctr: 'ac_ctr',
        CLASS_ac_ctr_left: 'ac_ctr_left',
        CLASS_ac_ctr_right: 'ac_ctr_right',
        CLASS_ac_garnish_yxa: 'ac_garnish_yxa',
        CLASS_ac_left: 'ac_left',
        CLASS_ac_right: 'ac_right',
        CLASS_cover_upper_yxa: 'cover_upper_yxa',
        CLASS_dashboard: 'dashboard',
        CLASS_garnish_drvr_inside_yl: 'garnish_drvr',
        CLASS_hazard_switches: 'hazard_switches',
        CLASS_key: 'key',
        CLASS_label_ac: 'label_ac',
        CLASS_lgt_wip_right: 'lgt_wip_right',
        CLASS_lower_panel: 'lower_panel',
        CLASS_nozzle_left: 'nozzle_left',
        CLASS_nozzle_right: 'nozzle_right',
        CLASS_orn_ctr: 'orn_ctr',
        CLASS_orn_drvr: 'orn_drvr',
        CLASS_push_button: 'push_button',
        CLASS_screen: 'gar_ip_ctr',
        CLASS_sensor_left: 'sensor_left',
        CLASS_sensor_right: 'sensor_right',
        CLASS_speedometer: 'speedometer',
        CLASS_steering_coil: 'steering_coil',
        CLASS_steering_cover: 'steering_cover',
        CLASS_switch: 'switch',
        CLASS_upper_panel: 'upper_panel',
        CLASS_usb_aux: 'usb_aux',
        CLASS_usb_aux_container: 'usb_aux_container',
        CLASS_lgt_wip_left: 'lgt_wip_left',
    }

    class_confidence = {
        CLASS_ac_control: 0.25,
        CLASS_ac_ctr: 0.25,
        CLASS_ac_ctr_left: 0.25,
        CLASS_ac_ctr_right: 0.25,
        CLASS_ac_garnish_yxa: 0.25,
        CLASS_ac_left: 0.25,
        CLASS_ac_right: 0.25,
        CLASS_cover_upper_yxa: 0.25,
        CLASS_dashboard: 0.25,
        CLASS_garnish_drvr_inside_yl: 0.25,
        CLASS_hazard_switches: 0.25,
        CLASS_key: 0.8,
        CLASS_label_ac: 0.25,
        CLASS_lgt_wip_right: 0.25,
        CLASS_lower_panel: 0.25,
        CLASS_nozzle_left: 0.25,
        CLASS_nozzle_right: 0.25,
        CLASS_orn_ctr: 0.25,
        CLASS_orn_drvr: 0.25,
        CLASS_push_button: 0.25,
        CLASS_screen: 0.25,
        CLASS_sensor_left: 0.25,
        CLASS_sensor_right: 0.25,
        CLASS_speedometer: 0.25,
        CLASS_steering_coil: 0.25,
        CLASS_steering_cover: 0.25,
        CLASS_switch: 0.25,
        CLASS_upper_panel: 0.25,
        CLASS_usb_aux: 0.25,
        CLASS_usb_aux_container: 0.25,
        CLASS_lgt_wip_left: 0.25,
    }

    class_colors = {k: color_green for k in class_names.keys()}

    class_cams = {
        CLASS_ac_control: {'top'},
        CLASS_ac_ctr: {'top'},
        CLASS_ac_ctr_left: {'top'},
        CLASS_ac_ctr_right: {'top'},
        CLASS_ac_garnish_yxa: {'top'},
        CLASS_ac_left: {'top'},
        CLASS_ac_right: {'top'},
        CLASS_cover_upper_yxa: {'up'},
        CLASS_dashboard: set(),
        CLASS_garnish_drvr_inside_yl: {'top', 'bottom'},
        CLASS_hazard_switches: {'top'},
        CLASS_key: {'bottom' },
        CLASS_label_ac: {'bottom'},
        CLASS_lgt_wip_right: {'top'},
        CLASS_lower_panel: {'bottom'},
        CLASS_nozzle_left: {'up'},
        CLASS_nozzle_right: {'up'},
        CLASS_orn_ctr: {'top'},
        CLASS_orn_drvr: {'top'},
        CLASS_push_button: {'top', 'bottom'},
        CLASS_screen: {'top'},
        CLASS_sensor_left: {'up'},
        CLASS_sensor_right: {'up'},
        CLASS_speedometer: {'top'},
        CLASS_steering_coil: {'top'},
        CLASS_steering_cover: {'bottom'},
        CLASS_switch: {'bottom'},
        CLASS_upper_panel: {'up'},
        CLASS_usb_aux: {'bottom'},
        CLASS_usb_aux_container: {'bottom'},
        CLASS_lgt_wip_left: {'top'},
    }

    @staticmethod
    def get_processed_class(class_name, vehicle_category, vehicle_type):
        return class_name
        # if class_name == PartDetectionModel.CLASS_lgt_wip_right:
        #     if vehicle_type == 'RHD':
        #         return PartDetectionModel.CLASS_lights
        #     elif vehicle_type == 'LHD':
        #         return PartDetectionModel.CLASS_wiper
        # elif class_name == PartDetectionModel.CLASS_lgt_wip_left:
        #     if vehicle_type == 'RHD':
        #         return PartDetectionModel.CLASS_wiper
        #     elif vehicle_type == 'LHD':
        #         return PartDetectionModel.CLASS_lights
        # else:
        #     return class_name