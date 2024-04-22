from ..colors import color_white, color_green

CLASS_orn_drv_yhbhc = '73832M73R00-R8R'
CLASS_orn_yhbhc = '73081M73R00-R8R'
CLASS_coil_sas_blue = '37410M68P10'
CLASS_cov_steer = '48400M55R00-R8R'
CLASS_pnl_instr_up_brn = '73111M72R00-R8R'
CLASS_sw_fuel = '37960M66R00'
CLASS_sw_option_hole = '37285M75J00'
CLASS_sw_esp_idstp_cam = '37585M66R00'
CLASS_sw_head_lamp_lvlng = '35180M66R00'
CLASS_w_speedometer = '34203M50UK0'
CLASS_outside_rhd = '73083M72R00-C48 '
CLASS_inside_rhd = '73082M72R00-C48'
CLASS_ac_asst_rhd = '73086M72R00-C48'
CLASS_hazard_warning = '37430M68P20-5PK'
CLASS_tuner_assy = '39101M72R04-ZCA'
CLASS_sw_lgt_trn_auto = '37210M72R00'
CLASS_sw_wpr_wsh = '37310M72R00'
CLASS_dashboard = 'dashboard'

class_names = [
    CLASS_ac_asst_rhd,
    CLASS_coil_sas_blue,
    CLASS_cov_steer,
    None, # dashboard
    CLASS_hazard_warning,
    CLASS_inside_rhd,
    CLASS_orn_drv_yhbhc,
    CLASS_orn_yhbhc,
    CLASS_outside_rhd,
    CLASS_pnl_instr_up_brn,
    CLASS_sw_esp_idstp_cam,
    CLASS_sw_fuel,
    CLASS_sw_head_lamp_lvlng,
    CLASS_sw_lgt_trn_auto,
    CLASS_sw_option_hole,
    CLASS_sw_wpr_wsh,
    CLASS_tuner_assy,
    CLASS_w_speedometer,
]

class_confidence = {
    CLASS_orn_drv_yhbhc: 0.25,
    CLASS_orn_yhbhc: 0.25,
    CLASS_coil_sas_blue: 0.25,
    CLASS_cov_steer: 0.25,
    CLASS_pnl_instr_up_brn: 0.25,
    CLASS_sw_fuel: 0.25,
    CLASS_sw_option_hole: 0.25,
    CLASS_sw_esp_idstp_cam: 0.25,
    CLASS_sw_head_lamp_lvlng: 0.25,
    CLASS_w_speedometer: 0.25,
    CLASS_outside_rhd: 0.25,
    CLASS_inside_rhd: 0.25,
    CLASS_ac_asst_rhd: 0.25,
    CLASS_hazard_warning: 0.25,
    CLASS_tuner_assy: 0.25,
    CLASS_sw_lgt_trn_auto: 0.25,
    CLASS_sw_wpr_wsh: 0.25,
    CLASS_dashboard: 0.25,
}

class_colors = {
    CLASS_orn_drv_yhbhc: color_green,
    CLASS_orn_yhbhc: color_green,
    CLASS_coil_sas_blue: color_green,
    CLASS_cov_steer: color_green,
    CLASS_pnl_instr_up_brn: color_green,
    CLASS_sw_fuel: color_green,
    CLASS_sw_option_hole: color_green,
    CLASS_sw_esp_idstp_cam: color_green,
    CLASS_sw_head_lamp_lvlng: color_green,
    CLASS_w_speedometer: color_green,
    CLASS_outside_rhd: color_green,
    CLASS_inside_rhd: color_green,
    CLASS_ac_asst_rhd: color_green,
    CLASS_hazard_warning: color_green,
    CLASS_tuner_assy: color_green,
    CLASS_sw_lgt_trn_auto: color_green,
    CLASS_sw_wpr_wsh: color_green,
    CLASS_dashboard: color_white,
}
