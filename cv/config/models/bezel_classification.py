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
        '73833M73R10-5PK',
    ]

    class_names = {
        '73831M79M00-V6N': ' BEZEL,I/P SW',
        '73831M79M10-V6N': ' BEZEL,I/P SW',
        '73831M79M20-V6N': ' BEZEL,I/P SW',
        '73833M73R00-5PK': ' BEZEL,I/P SW',
        '73833M73R10-5PK': ' BEZEL,I/P SW',
    }

    class_colors = {
        '73831M79M00-V6N': color_green,
        '73831M79M10-V6N': color_green,
        '73831M79M20-V6N': color_green,
        '73833M73R00-5PK': color_green,
        '73833M73R10-5PK': color_green,
    }