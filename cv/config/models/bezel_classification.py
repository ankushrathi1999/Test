from .bezel_group_detection import BezelGroupDetectionModel
from ..colors import color_white, color_green

part_bezel_group_lookup = {
    ('bezel_yhbc_black_no_key', 'RHD'): '73833M73R00-5PK',
    ('bezel_yhbc_black_no_key', 'LHD'): '73833M73R50-5PK',
    ('bezel_yl1_beige_no_key', 'RHD'): '73831M79M00-V6N',
    ('bezel_yl1_beige_no_key', 'LHD'): '73831M79M10-V6N',
    ('bezel_yl1_black_no_key', 'RHD'): '73831M79M00-5PK',
    ('bezel_yl1_black_no_key', 'LHD'): '73831M79M10-5PK',
}

class BezelClassificationModel:
    name = 'bezel_classification'
    imgsz = 256
    target_detections = {BezelGroupDetectionModel.CLASS_CONTAINER}

    ordered_class_list = [
        '73833M73R00-V6N',
        '73833M73R10-5PK',
        '73833M73R10-V6N',
        '73831M79M20-V6N',
        '73826M66T00-5PK',
        '73826M66T10-5PK',
        'bezel_yhbc_black_no_key',
        'bezel_yl1_beige_no_key',
        'bezel_yl1_black_no_key',
    ]

    class_names = {
        '73833M73R00-V6N': 'BEIGE W/O HOLE, BEZEL YHB',
        '73833M73R10-5PK': 'BLACK W/ HOLE, BEZEL YHBC',
        '73833M73R10-V6N': 'BEIGE W/ HOLE, BEZEL YHB',
        '73831M79M20-V6N': 'BEIGE W/ HOLE, BEZEL YL1',
        '73826M66T00-5PK': '7 HOLES, BEZEL YXA',
        '73826M66T10-5PK': '10 HOLES, BEZEL YXA',
        'bezel_yhbc_black_no_key': 'BLACK W/O HOLE, BEZEL YHB',
        'bezel_yl1_beige_no_key': 'BEIGE W/O HOLE, BEZEL YL1',
        'bezel_yl1_black_no_key': 'BLACK W/O HOLE, BEZEL YL1',
    }

    class_colors = {k: color_green for k in ordered_class_list}

    @staticmethod
    def get_part_number(detection_label, class_name, vehicle_category, vehicle_type):
        return part_bezel_group_lookup.get((class_name, vehicle_type), class_name)