from .bezel_group_detection import BezelGroupDetectionModel
from ..colors import color_white, color_green

class BezelClassificationModel:
    name = 'bezel_classification'
    imgsz = 256
    target_detections = {BezelGroupDetectionModel.CLASS_CONTAINER}

    ordered_class_list = [
        '73831M79M00-V6N',
        '73831M79M10-V6N',
        '73831M79M20-V6N',
        '73833M73R00-5PK',
        '73833M73R00-V6N',
        '73833M73R10-5PK',
        '73833M73R10-V6N',
    ]

    class_names = {
        '73831M79M00-V6N': 'BEIGE W/O HOLE, BEZEL YL1',
        '73831M79M10-V6N': 'BEIGE W/O HOLE, BEZEL YL1',
        '73831M79M20-V6N': 'BEIGE W/ HOLE, BEZEL YL1',
        '73833M73R00-5PK': 'BLACK W/O HOLE, BEZEL YHB',
        '73833M73R00-V6N': 'BEIGE W/O HOLE, BEZEL YHB',
        '73833M73R10-5PK': 'BLACK W/ HOLE, BEZEL YHBC',
        '73833M73R10-V6N': 'BEIGE W/ HOLE, BEZEL YHB',
    }

    class_colors = {
        '73831M79M00-V6N': color_green,
        '73831M79M10-V6N': color_green,
        '73831M79M20-V6N': color_green,
        '73833M73R00-5PK': color_green,
        '73833M73R00-V6N': color_green,
        '73833M73R10-5PK': color_green,
        '73833M73R10-V6N': color_green,
    }