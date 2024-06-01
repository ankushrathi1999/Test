from ..colors import color_white, color_green

class PartDetectionModel:
    name = 'part_detection'
    imgsz = 640
    target_cams = {'top', 'bottom', 'up'}

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
    CLASS_lights = name + '_lights'
    CLASS_lower_panel = name + '_lower_panel'
    CLASS_orn_ctr = name + '_orn_ctr'
    CLASS_orn_drvr = name + '_orn_drvr'
    CLASS_push_button = name + '_push_button'
    CLASS_screen = name + '_screen'
    CLASS_sensor = name + '_sensor'
    CLASS_speedometer = name + '_speedometer'
    CLASS_steering_coil = name + '_steering_coil'
    CLASS_steering_cover = name + '_steering_cover'
    CLASS_switch = name + '_switch'
    CLASS_upper_panel = name + '_upper_panel'
    CLASS_usb_aux = name + '_usb_aux'
    CLASS_usb_aux_container = name + '_usb_aux_container'
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
        CLASS_key,
        CLASS_label_ac,
        CLASS_lights,
        CLASS_lower_panel,
        CLASS_orn_ctr,
        CLASS_orn_drvr,
        CLASS_push_button,
        CLASS_screen,
        CLASS_sensor,
        CLASS_speedometer,
        CLASS_steering_coil,
        CLASS_steering_cover,
        CLASS_switch,
        CLASS_upper_panel,
        CLASS_usb_aux,
        CLASS_usb_aux_container,
        CLASS_wiper,
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
        CLASS_lights: 'lights',
        CLASS_lower_panel: 'lower_panel',
        CLASS_orn_ctr: 'orn_ctr',
        CLASS_orn_drvr: 'orn_drvr',
        CLASS_push_button: 'push_button',
        CLASS_screen: 'screen',
        CLASS_sensor: 'sensor',
        CLASS_speedometer: 'speedometer',
        CLASS_steering_coil: 'steering_coil',
        CLASS_steering_cover: 'steering_cover',
        CLASS_switch: 'switch',
        CLASS_upper_panel: 'upper_panel',
        CLASS_usb_aux: 'usb_aux',
        CLASS_usb_aux_container: 'usb_aux_container',
        CLASS_wiper: 'wiper',
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
        CLASS_key: 0.25,
        CLASS_label_ac: 0.25,
        CLASS_lights: 0.25,
        CLASS_lower_panel: 0.25,
        CLASS_orn_ctr: 0.25,
        CLASS_orn_drvr: 0.25,
        CLASS_push_button: 0.25,
        CLASS_screen: 0.25,
        CLASS_sensor: 0.25,
        CLASS_speedometer: 0.25,
        CLASS_steering_coil: 0.25,
        CLASS_steering_cover: 0.25,
        CLASS_switch: 0.25,
        CLASS_upper_panel: 0.25,
        CLASS_usb_aux: 0.25,
        CLASS_usb_aux_container: 0.25,
        CLASS_wiper: 0.25,
    }

    class_colors = {
        CLASS_ac_control: color_green,
        CLASS_ac_ctr: color_green,
        CLASS_ac_ctr_left: color_green,
        CLASS_ac_ctr_right: color_green,
        CLASS_ac_garnish_yxa: color_green,
        CLASS_ac_left: color_green,
        CLASS_ac_right: color_green,
        CLASS_cover_upper_yxa: color_green,
        CLASS_dashboard: color_green,
        CLASS_garnish_drvr_inside_yl: color_green,
        CLASS_hazard_switches: color_green,
        CLASS_key: color_green,
        CLASS_label_ac: color_green,
        CLASS_lights: color_green,
        CLASS_lower_panel: color_green,
        CLASS_orn_ctr: color_green,
        CLASS_orn_drvr: color_green,
        CLASS_push_button: color_green,
        CLASS_screen: color_green,
        CLASS_sensor: color_green,
        CLASS_speedometer: color_green,
        CLASS_steering_coil: color_green,
        CLASS_steering_cover: color_green,
        CLASS_switch: color_green,
        CLASS_upper_panel: color_green,
        CLASS_usb_aux: color_green,
        CLASS_usb_aux_container: color_green,
        CLASS_wiper: color_green,
    }