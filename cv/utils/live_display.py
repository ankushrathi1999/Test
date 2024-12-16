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
        'color_code': dashboard.color_code if has_dashboard else '-',
        'result': ("OK" if overall_ok else "NG") if has_dashboard else None,
        'is_ended': dashboard.is_ended if has_dashboard else False,
        'parts': [{
            "title": part['part_name_long'][:100], # 100 char limit on part names
            "is_ok": part['result'] == DetectionResult.OK
        } for part in parts[:40]] # max 40 parts can be displayed
    }

def get_positions(img_h):
    ref_h = 1080
    positions = {
        'cam_row1_y': 168,
        'cam_row2_y': 624,

        'cam_padding_x': 4,
        'cam_header_offset_y': 32,
        'cam_width': 433,

        'stats_row1_y': 150,
        'stats_row2_y': 605,

        'metadata_title_offset_y': 36,
        'metadata_value_offset_y': 60,
        'metadata_col1_offset_x': 0,
        'metadata_col2_offset_x': 60,
        'metadata_col3_offset_x': 255,
        'metadata_col4_offset_x': 255+180,

        'parts_offset_y': 96,
        'parts_padding_x': 10,
        'parts_cell_width': 280,
        'parts_cell_height': 36,
        'parts_cell_text_offset_x': 8,
        'parts_cell_text_offset_y': 2,
        'parts_cell_icon_offset_x': 20,
        'parts_cell_icon_offset_y': 16,
        'parts_cell_icon_radius': 8,

        'result_offset_y': 350,
        'result_box_offset_y': 30,
        'result_box_height': 36,
        'result_box_width': 439+132,
        'result_box_text_offset_y': 35,
        'result_box_text_offset_x_ok': 200+61,
        'result_box_text_offset_x_ng': 150+61,
    }
    return {k: round(v*img_h/ref_h) for k, v in positions.items()}

def draw_text(img, text, text_pos, font = cv2.FONT_HERSHEY_SIMPLEX, font_scale = 0.5, text_thickness = 1, text_color = (0,0,0)):
    x, y = text_pos
    cv2.putText(img, text, (x, y+20), font, font_scale, text_color, text_thickness, cv2.LINE_AA)
            
def prepare_live_display(frames, data):
    bg_img = cv2.imread('./config/background_v2.jpg')
    target_width = 1920
    target_height = 1080
    
    # Data and postions
    positions = get_positions(target_height)
    artifacts = data.artifacts if len(data.artifacts) > 0 else data.artifacts_prev
    data = [prepare_dashbord_data(artifacts[i] if len(artifacts) > i else None) for i in range(2)]

    # Resize background
    bg_img = cv2.resize(bg_img, (target_width, target_height))

    # Render Cameras with header
    for i, cam_type in enumerate([
        'RH_IN_BOTTOM', 'RH_IN_TOP', 'RH_OUT',
        'LH_IN_BOTTOM', 'LH_IN_TOP', 'LH_OUT',
    ]):
        row_num = 1 if i < 3 else 2
        col_num = (i % 3) + 1
        frame_cam = frames[cam_type]
        image_width = positions['cam_width']
        image_height = int((image_width / frame_cam.shape[1]) * frame_cam.shape[0])

        # Render heading
        header_x = (positions['cam_padding_x'] * (col_num)) + (image_width * (col_num-1))
        header_y = positions['cam_row1_y' if row_num == 1 else 'cam_row2_y']
        draw_text(bg_img, f"Camera: {cam_type.replace('_', ' ')}", (header_x, header_y), font=cv2.FONT_HERSHEY_TRIPLEX, font_scale=0.6)

        # Render image
        frame_cam = cv2.resize(frame_cam, (image_width, image_height)) # Resized frame
        frame_x = (positions['cam_padding_x'] * (col_num)) + (image_width * (col_num-1))
        frame_y = positions['cam_row1_y' if row_num == 1 else 'cam_row2_y'] + positions['cam_header_offset_y']
        print(cam_type, frame_x, frame_y)
        bg_img[frame_y: frame_y + frame_cam.shape[0], frame_x: frame_x + frame_cam.shape[1]] = frame_cam

    # Estimate stats x position
    stats_x = (image_width * 3) + (positions['cam_padding_x'] * 4) + positions['parts_padding_x']

    # Part Boxes
    for i in range(2):
        row_num = i+1
        for i, part in enumerate(data[i]['parts']):
            part_col_num = (i // 7) + 1
            part_row_num = (i % 7) + 1
            if part_col_num > 2:
                break

            # Render box
            box_x1 = stats_x + ((positions['parts_cell_width'] + positions['parts_padding_x']) * (part_col_num-1)) 
            box_x2 = box_x1 + positions['parts_cell_width']
            box_y1 = positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['parts_offset_y'] + (positions['parts_cell_height'] * (part_row_num-1))
            box_y2 = box_y1 + positions['parts_cell_height']
            box_color = (229,240,215) if part["is_ok"] else (214,221,255)
            cv2.rectangle(bg_img, (box_x1, box_y1), (box_x2, box_y2), box_color, -1)

            # Render Text
            text_x = box_x1 + positions['parts_cell_text_offset_x']
            text_y = box_y1 + positions['parts_cell_text_offset_y']
            draw_text(bg_img, part["title"], (text_x, text_y), font_scale=0.4)

            # Render Icon
            icon_radius =  positions['parts_cell_icon_radius']
            icon_center_x = box_x2 - positions['parts_cell_icon_offset_x']
            icon_center_y = box_y1 + positions['parts_cell_icon_offset_y']
            if part["is_ok"]: # tick icon
                cv2.circle(bg_img, (icon_center_x, icon_center_y), icon_radius, (105,149,45), 1)
                check_start = (icon_center_x - int(icon_radius * 0.6), icon_center_y + int(icon_radius * 0.1))
                check_mid = (icon_center_x - int(icon_radius * 0.2), icon_center_y + int(icon_radius * 0.6))
                check_end = (icon_center_x + int(icon_radius * 0.5), icon_center_y - int(icon_radius * 0.4))
                cv2.line(bg_img, check_start, check_mid, (105,149,45), thickness=1)
                cv2.line(bg_img, check_mid, check_end, (105,149,45), thickness=1)
            else: # cross icon
                cv2.circle(bg_img, (icon_center_x, icon_center_y), icon_radius, (40,72,212), 1)
                cross_start1 = (icon_center_x - int(icon_radius * 0.5), icon_center_y - int(icon_radius * 0.5))
                cross_end1 = (icon_center_x + int(icon_radius * 0.5), icon_center_y + int(icon_radius * 0.5))
                cross_start2 = (icon_center_x + int(icon_radius * 0.5), icon_center_y - int(icon_radius * 0.5))
                cross_end2 = (icon_center_x - int(icon_radius * 0.5), icon_center_y + int(icon_radius * 0.5))
                cv2.line(bg_img, cross_start1, cross_end1, (40,72,212), thickness=1)
                cv2.line(bg_img, cross_start2, cross_end2, (40,72,212), thickness=1)


    # Result Boxes
    for i in range(2):
        row_num = i+1
        if data[i]['result']:
            # Render heading
            header_x = stats_x
            header_y = positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['result_offset_y']
            # draw_text(bg_img, 'RESULT', (header_x, header_y), font=cv2.FONT_HERSHEY_TRIPLEX)

            # Render Box
            box_x1 = stats_x
            box_x2 = box_x1 + positions['result_box_width']
            box_y1 = positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['result_offset_y'] + positions['result_box_offset_y']
            box_y2 = box_y1 + positions['result_box_height']
            result = data[i]['result']
            is_small_text = True
            if result == 'NG' and not data[i]['is_ended']:
                result = 'PROGRESS'
                is_small_text = False
            box_color = {
                'OK': (105,149,45),
                'NG': (52, 64, 235),
                'PROGRESS': (52, 64, 235), # todo: change color
            }[result]
            box_text = {
                'OK': 'OK',
                'NG': 'NG',
                'PROGRESS': 'INSPECTING'
            }[result]
            cv2.rectangle(bg_img, (box_x1, box_y1), (box_x2, box_y2), box_color, -1)

            # Render Box Text
            text_x = stats_x + positions['result_box_text_offset_x_ok' if is_small_text else 'result_box_text_offset_x_ng']
            text_y = positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['result_offset_y'] + positions['result_box_text_offset_y']
            draw_text(bg_img, box_text, (text_x, text_y), font=cv2.FONT_HERSHEY_TRIPLEX, font_scale=0.7, text_thickness=2, text_color=(255,255,255))


    # Text elements
    for i in range(2):
        row_num = i+1
        text_items = [
            {
                'text': 'Vehicle Details',
                'text_pos': (stats_x, positions['stats_row1_y' if row_num == 1 else 'stats_row2_y']),
                'font': cv2.FONT_HERSHEY_TRIPLEX,
                'font_scale': 0.6
            },
            {
                'text': 'PSN',
                'text_pos': (
                    stats_x + positions['metadata_col1_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_title_offset_y']
                ),
                'text_color': (132,119,112)
            },
            {
                'text': data[i]['psn'],
                'text_pos': (
                    stats_x + positions['metadata_col1_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_value_offset_y']
                ),
                'font': cv2.FONT_HERSHEY_TRIPLEX
            },
            {
                'text': 'CHASSIS NUMBER',
                'text_pos': (
                    stats_x + positions['metadata_col2_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_title_offset_y']
                ),
                'text_color': (132,119,112)
            },
            {
                'text': data[i]['chassis'],
                'text_pos': (
                    stats_x + positions['metadata_col2_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_value_offset_y']
                ),
                'font': cv2.FONT_HERSHEY_TRIPLEX
            },
            {
                'text': 'VEHICLE MODEL',
                'text_pos': (
                    stats_x + positions['metadata_col3_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_title_offset_y']
                ),
                'text_color': (132,119,112)
            },
            {
                'text': data[i]['vehicle_model'],
                'text_pos': (
                    stats_x + positions['metadata_col3_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_value_offset_y']
                ),
                'font': cv2.FONT_HERSHEY_TRIPLEX
            },
             {
                'text': 'COLOR CODE',
                'text_pos': (
                    stats_x + positions['metadata_col4_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_title_offset_y']
                ),
                'text_color': (132,119,112)
            },
            {
                'text': data[i]['color_code'],
                'text_pos': (
                    stats_x + positions['metadata_col4_offset_x'],
                    positions['stats_row1_y' if row_num == 1 else 'stats_row2_y'] + positions['metadata_value_offset_y']
                ),
                'font': cv2.FONT_HERSHEY_TRIPLEX
            }
        ]

        for item in text_items:
            text = item.pop('text')
            text_pos = item.pop('text_pos')
            draw_text(bg_img, text, text_pos, **item)

    return bg_img