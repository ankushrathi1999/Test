import cv2

from api.detection import DetectionResult

def prepare_dashbord_data(dashboard):
    has_dashboard = dashboard is not None
    if has_dashboard:
        parts, overall_ok = dashboard.get_part_results()
    else:
        parts = []
        overall_ok = None
    return {
        'psn': str(dashboard.psn) if has_dashboard else '-',
        'chassis': dashboard.chassis if has_dashboard else '-',
        'vehicle_model': dashboard.vehicle_model if has_dashboard else '-',
        'result': ("OK" if overall_ok else "NG") if has_dashboard else None,
        'parts': [{
            "title": (part.get('part_name_long') or part['part_name'])[:40], # 40 char limit on part names
            "is_ok": part['result'] == DetectionResult.OK
        } for part in parts[:40]] # max 40 parts can be displayed
    }

def get_positions(img_h):
    ref_h = 1080
    positions = {
        'header_height': 108,
        'camera_offset': 140,
        'horizontal_padding': 24,

        'title_bottom_header_y': 636,
        'title_psn_y': 680,
        'value_psn_y': 706,
        'title_chassis_y': 744,
        'value_chassis_y': 770,
        'title_model_y': 808,
        'value_model_y': 834,
        'title_result_y': 964,
        'value_result_box_y': 992,
        'value_result_box_height': 48,
        'value_result_box_width': 292,
        'value_result_x': 155,
        'value_result_y': 1002,

        'parts_col1_x': 340,
        'parts_col2_x': 735,
        'parts_col3_x': 1130,
        'parts_col4_x': 1525,
        'col_width': 371,
        'col_height': 36,
        'col_start_y': 680,

        'cell_text_offset_x': 8,
        'cell_text_offset_y': 8,
        'cell_icon_offset_x': 10,
        'cell_icon_radius': 8,
    }
    return {k: round(v*img_h/ref_h) for k, v in positions.items()}

def draw_text(img, text, text_pos, font = cv2.FONT_HERSHEY_SIMPLEX, font_scale = 0.5, text_thickness = 1, text_color = (0,0,0)):
    x, y = text_pos
    cv2.putText(img, text, (x, y+20), font, font_scale, text_color, text_thickness, cv2.LINE_AA)
            
def prepare_live_display(frame_top, frame_bottom, frame_up, data):
    bg_img = cv2.imread('./config/background_v2.jpg')
    target_width = 1920
    target_height = 1080
    
    # Data and postions
    positions = get_positions(target_height)
    data = prepare_dashbord_data(data.artifact)
    n_images = 3

    image_width = (target_width - ((n_images+1)*positions['horizontal_padding'])) // 3
    image_height = int((image_width / frame_top.shape[1]) * frame_top.shape[0])

    frame_top = cv2.resize(frame_top, (image_width, image_height))
    frame_bottom = cv2.resize(frame_bottom, (image_width, image_height))
    frame_up = cv2.resize(frame_up, (image_width, image_height))
    bg_img = cv2.resize(bg_img, (target_width, target_height))

    # Video Layout
    x_offset = positions['horizontal_padding']
    y_offset = positions['camera_offset']
    draw_text(bg_img, 'Camera 01:', (x_offset, positions['header_height']))
    bg_img[y_offset: y_offset + frame_top.shape[0], x_offset: x_offset + frame_top.shape[1]] = frame_top

    x_offset = image_width + (positions['horizontal_padding']*2)
    draw_text(bg_img, 'Camera 02:', (x_offset, positions['header_height']))
    bg_img[y_offset: y_offset + frame_bottom.shape[0], x_offset: x_offset + frame_bottom.shape[1]] = frame_bottom

    x_offset = (image_width*2) + (positions['horizontal_padding']*3)
    draw_text(bg_img, 'Camera 03:', (x_offset, positions['header_height']))
    bg_img[y_offset: y_offset + frame_up.shape[0], x_offset: x_offset + frame_up.shape[1]] = frame_up

    # Result Box
    if data['result']:
        x1 = positions['horizontal_padding']
        x2 = x1 + positions['value_result_box_width']
        y1 = positions['value_result_box_y']
        y2 = y1 + positions['value_result_box_height']
        box_color = {
            'OK': (105,149,45),
            'NG': (52, 64, 235),
        }[data['result']]
        cv2.rectangle(bg_img, (x1, y1), (x2, y2), box_color, -1)
        draw_text(bg_img, 'RESULT', (positions['horizontal_padding'], positions['title_result_y']), font=cv2.FONT_HERSHEY_TRIPLEX)
        draw_text(
            bg_img, data['result'], (positions['value_result_x'], positions['value_result_y']),
            font=cv2.FONT_HERSHEY_TRIPLEX, font_scale=0.7, text_thickness=2, text_color=(255,255,255))

    for i, part in enumerate(data['parts']):
        col_num = i // 10
        row_num = i % 10
        x1 = positions[f'parts_col{col_num+1}_x']
        x2 = x1 + positions['col_width']
        y1 = positions['col_start_y'] + row_num * positions['col_height']
        y2 = y1 + positions['col_height']
        color = (229,240,215) if part["is_ok"] else (214,221,255)
        cv2.rectangle(bg_img, (x1, y1), (x2, y2), color, -1)
        draw_text(bg_img, part["title"], (x1+positions['cell_text_offset_x'], y1+positions['cell_text_offset_y']))
        radius = positions['cell_icon_radius']
        center = (x2 - (positions['cell_icon_offset_x']+radius), int((y1+y2)/2))
        if part["is_ok"]: # tick icon
            cv2.circle(bg_img, center, radius, (105,149,45), 1)
            check_start = (center[0] - int(radius * 0.6), center[1] + int(radius * 0.1))
            check_mid = (center[0] - int(radius * 0.2), center[1] + int(radius * 0.6))
            check_end = (center[0] + int(radius * 0.5), center[1] - int(radius * 0.4))
            cv2.line(bg_img, check_start, check_mid, (105,149,45), thickness=1)
            cv2.line(bg_img, check_mid, check_end, (105,149,45), thickness=1)
        else: # cross icon
            cv2.circle(bg_img, center, radius, (40,72,212), 1)
            cross_start1 = (center[0] - int(radius * 0.5), center[1] - int(radius * 0.5))
            cross_end1 = (center[0] + int(radius * 0.5), center[1] + int(radius * 0.5))
            cross_start2 = (center[0] + int(radius * 0.5), center[1] - int(radius * 0.5))
            cross_end2 = (center[0] - int(radius * 0.5), center[1] + int(radius * 0.5))
            cv2.line(bg_img, cross_start1, cross_end1, (40,72,212), thickness=1)
            cv2.line(bg_img, cross_start2, cross_end2, (40,72,212), thickness=1)

    # Text elements
    text_items = [
        {'text': 'Vehicle Details', 'text_pos': (positions['horizontal_padding'], positions['title_bottom_header_y']), 'font': cv2.FONT_HERSHEY_TRIPLEX, 'font_scale': 0.6},
        {'text': 'Parts', 'text_pos': (positions['parts_col1_x'], positions['title_bottom_header_y']), 'font': cv2.FONT_HERSHEY_TRIPLEX, 'font_scale': 0.6},
        {'text': 'PSN', 'text_pos': (positions['horizontal_padding'], positions['title_psn_y']), 'text_color': (132,119,112)},
        {'text': data['psn'], 'text_pos': (positions['horizontal_padding'], positions['value_psn_y']), 'font': cv2.FONT_HERSHEY_TRIPLEX},
        {'text': 'CHASSIS NUMBER', 'text_pos': (positions['horizontal_padding'], positions['title_chassis_y']), 'text_color': (132,119,112)},
        {'text': data['chassis'], 'text_pos': (positions['horizontal_padding'], positions['value_chassis_y']), 'font': cv2.FONT_HERSHEY_TRIPLEX},
        {'text': 'VEHICLE MODEL', 'text_pos': (positions['horizontal_padding'], positions['title_model_y']), 'text_color': (132,119,112)},
        {'text': data['vehicle_model'], 'text_pos': (positions['horizontal_padding'], positions['value_model_y']), 'font': cv2.FONT_HERSHEY_TRIPLEX},
    ]

    for item in text_items:
        text = item.pop('text')
        text_pos = item.pop('text_pos')
        draw_text(bg_img, text, text_pos, **item)

    return bg_img