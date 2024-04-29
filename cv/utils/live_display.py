import cv2

from api.artifact import part_success_threshold
from api.state import PLC_STATES, get_state_name, get_plc_state_name
from .image_utils import draw_stats
from config.colors import color_red, color_green


def prepare_dashboard_stats(dashboard):
    col1 = [
        {
            "type": "heading",
            "title": "VEHICLE DETAILS",
        },
        {
            "title": "PSN",
            "value": dashboard.psn,
        },
        {
            "title": "Chassis",
            "value": dashboard.chassis,
        },
        {
            "title": "Model",
            "value": dashboard.vehicle_model,
            "color": color_green if dashboard.inspection_flag == 1 else color_red
        },
    ]

    part_cols = []
    for i in range(5):
        cur_col = []
        for j in range(5):
            cur_part_idx = (i*5) + j
            if cur_part_idx >= len(dashboard.part_list):
                cur_col.append({
                    "type": "message",
                    "title": "",
                })
            else:
                cur_part = dashboard.part_list[cur_part_idx]
                cur_col.append({
                    "type": "message",
                    "title": cur_part,
                    "color": color_green if dashboard.part_counts[cur_part] >= part_success_threshold else color_red,
                    "fontScale": 0.8,
                    "textThickness": 1,
                })
        part_cols.append(cur_col)

    overall_ok = dashboard.part_ok_count >= len(dashboard.part_list)
    part_cols[-1][-1] = {
        "title": "RESULT",
        "value": "OK" if overall_ok else "NG",
        "fontScale": 1,
        "textThickness": 2,
        "color": color_green if overall_ok else color_red,
    }
   
    return [col1, [], *part_cols]

def prepare_waiting_stats(data):
    col1 = [
        {
            "type": "heading",
            "title": "Inspection Details",
        },
        {
            "title": "Status",
            "value": get_state_name(data.state.state),
        },
        {
            "title": "PLC",
            "value": get_plc_state_name(data.state.plc_state),
            "color": color_green if data.state.plc_state == PLC_STATES.HEALTHY else color_red
        },
    ]
    col2 = col3  = []
    col4 = [
        {
            "type": "heading",
            "title": "Keyboard Shortcuts",
        },
        {
            "title": "ESC",
            "value": "Quit Application"
        }
    ]
    return [col1, col2, col3, col4]    

def prepare_live_display(frame_top, frame_bottom, data):
    bg_img = cv2.imread('./config/background.jpg')
    target_width = 1920
    target_height = 1080
    header_offset = 150

    image_width = (target_width // 2) - 45
    image_height = int((image_width / frame_top.shape[1]) * frame_top.shape[0])

    frame_top = cv2.resize(frame_top, (image_width, image_height))
    frame_bottom = cv2.resize(frame_bottom, (image_width, image_height))
    bg_img = cv2.resize(bg_img, (target_width, target_height))

    x_offset = 30
    y_offset = header_offset
    bg_img[y_offset: y_offset + frame_top.shape[0], x_offset: x_offset + frame_top.shape[1]] = frame_top

    x_offset = image_width + 60
    y_offset = header_offset
    bg_img[y_offset: y_offset + frame_bottom.shape[0], x_offset: x_offset + frame_bottom.shape[1]] = frame_bottom

    if data.artifact is None:
        stats = prepare_waiting_stats(data)
    else:
        stats = prepare_dashboard_stats(data.artifact)
    draw_stats(bg_img, stats, global_font_scale=0.6)

    return bg_img
            
