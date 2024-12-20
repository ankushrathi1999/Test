from .part_detection_out import PartDetectionOutModel
from ..colors import color_green, color_red

body_color_lookup = {
    'ERU': 'ZZK',
    'E85': 'WBE',
    'E86': 'WBG',
    'FPK': 'ZZK',
    'E5R': 'WAA',
    'FFZ': 'WBF',
    'FRH': 'ZQK',
}

roof_color_lookup = {
    'ERU': 'ZHJ',
    'E85': 'WB3',
    'E86': 'WB3',
    'FPK': 'WB3',
    'E5R': 'WB3',
    'FFZ': 'WB3',
    'FRH': 'WB3',
}

def check_chrome_handle(artifact):
    desc = artifact.vehicle_description.lower()
    if artifact.vehicle_category == 'YHB':
        return 'zxi' in desc
    elif artifact.vehicle_category in {'YHC', 'YL1'}:
        return 'alpha' in desc
    return False

class ColorClassificationModel:
    name = 'color_classification'
    imgsz = 64
    target_detections = {PartDetectionOutModel.CLASS_MIRROR, PartDetectionOutModel.CLASS_HNDL}

    ordered_class_list = [
        'Chrome',
        'WAA',
        'WB3',
        'WBE',
        'WBF',
        'WBH',
        'Z7Q',
        'ZHJ',
        'ZQK',
        'ZYA',
        'ZYY',
        'black',
    ]

    class_names = {k: k for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}

    @staticmethod
    def get_part_number(detection_class, class_name, artifact):
        vehicle_color = artifact.color_code
        if detection_class == PartDetectionOutModel.CLASS_MIRROR:
            mirror_color_spec = roof_color_lookup.get(vehicle_color, vehicle_color)
            return mirror_color_spec, class_name
        elif detection_class == PartDetectionOutModel.CLASS_HNDL:
            handle_color_spec = body_color_lookup.get(vehicle_color, vehicle_color)
            if check_chrome_handle(artifact):
                handle_color_spec = 'Chrome'
            return handle_color_spec, class_name