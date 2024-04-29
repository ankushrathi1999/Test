from ..colors import color_white, color_green

CLASS_bez_ip_sw = '73833M73R00-V6N'
CLASS_lockset = '37019M72R00'
CLASS_pnl_hvac_yhbhc = '74400M72R20-V6N'
CLASS_pnl_instr_low = '73121M72R00-V6N'
CLASS_skt_usb_yhbhcxal1 = '39105M56R00-5PK'
CLASS_socket = '39440M56R20-5PK'
CLASS_dashboard = 'dashboard'

class_names = [
    CLASS_bez_ip_sw,
    None, # Dashboard
    CLASS_lockset,
    CLASS_pnl_hvac_yhbhc,
    CLASS_pnl_instr_low,
    CLASS_skt_usb_yhbhcxal1,
    CLASS_socket,
]

class_desc = {
    CLASS_bez_ip_sw: 'bez_ip_sw',
    CLASS_lockset: 'lockset',
    CLASS_pnl_hvac_yhbhc: 'pnl_hvac_yhbhc',
    CLASS_pnl_instr_low: 'pnl_instr_low',
    CLASS_skt_usb_yhbhcxal1: 'skt_usb_yhbhcxal1',
    CLASS_socket: 'socket',
    CLASS_dashboard: 'dashboard',
}

class_confidence = {
    CLASS_bez_ip_sw: 0.25,
    CLASS_lockset: 0.25,
    CLASS_pnl_hvac_yhbhc: 0.25,
    CLASS_pnl_instr_low: 0.25,
    CLASS_skt_usb_yhbhcxal1: 0.25,
    CLASS_socket: 0.25,
    CLASS_dashboard: 0.25,
}

class_colors = {
    CLASS_bez_ip_sw: color_green,
    CLASS_lockset: color_green,
    CLASS_pnl_hvac_yhbhc: color_green,
    CLASS_pnl_instr_low: color_green,
    CLASS_skt_usb_yhbhcxal1: color_green,
    CLASS_socket: color_green,
    CLASS_dashboard: color_white,
}
