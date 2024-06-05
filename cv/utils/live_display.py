import cv2

from api.artifact import part_success_threshold
from api.state import PLC_STATES, get_state_name, get_plc_state_name
from .image_utils import draw_stats
from config.colors import color_red, color_black
from api.detection import DetectionResult


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
            "color": color_black if dashboard.inspection_flag == 1 else color_red
        },
    ]

    parts, overall_ok = dashboard.get_part_results()

    part_cols = []
    for i in range(5):
        cur_col = []
        for j in range(5):
            cur_part_idx = (i*5) + j
            if cur_part_idx >= len(parts):
                cur_col.append({
                    "type": "message",
                    "title": "",
                })
            else:
                cur_part = parts[cur_part_idx]
                cur_part_desc = cur_part['part_name'][:20]
                cur_part_ok = cur_part['result'] == DetectionResult.OK
                cur_col.append({
                    "type": "message",
                    "title": cur_part_desc,
                    "color": color_black if cur_part_ok else color_red,
                    "fontScale": 0.6,
                    "textThickness": 1,
                })
        part_cols.append(cur_col)

    part_cols[-1][-1] = {
        "title": "RESULT",
        "value": "OK" if overall_ok else "NG",
        "fontScale": 1,
        "textThickness": 2,
        "color": color_black if overall_ok else color_red,
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
            "color": color_black if data.state.plc_state == PLC_STATES.HEALTHY else color_red
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

def prepare_live_display(frame_top, frame_bottom, frame_up, data):
    bg_img = cv2.imread('./config/background.jpg')
    target_width = 1920
    target_height = 1080
    header_offset = 250

    image_width = (target_width - 80) // 3
    image_height = int((image_width / frame_top.shape[1]) * frame_top.shape[0])

    frame_top = cv2.resize(frame_top, (image_width, image_height))
    frame_bottom = cv2.resize(frame_bottom, (image_width, image_height))
    frame_up = cv2.resize(frame_up, (image_width, image_height))
    bg_img = cv2.resize(bg_img, (target_width, target_height))

    x_offset = 20
    y_offset = header_offset
    bg_img[y_offset: y_offset + frame_top.shape[0], x_offset: x_offset + frame_top.shape[1]] = frame_top

    x_offset = image_width + 40
    y_offset = header_offset
    bg_img[y_offset: y_offset + frame_bottom.shape[0], x_offset: x_offset + frame_bottom.shape[1]] = frame_bottom

    x_offset = image_width*2 + 60
    y_offset = header_offset
    bg_img[y_offset: y_offset + frame_up.shape[0], x_offset: x_offset + frame_up.shape[1]] = frame_up

    if data.artifact is None:
        stats = prepare_waiting_stats(data)
    else:
        stats = prepare_dashboard_stats(data.artifact)
    draw_stats(bg_img, stats, global_font_scale=0.6)

    return bg_img
            
