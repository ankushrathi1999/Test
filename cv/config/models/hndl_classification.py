# from .part_detection_in_top import PartDetectionInTopModel
from .part_detection_out import PartDetectionOutModel
from ..colors import color_green, color_red

class HndlClassificationModel:
    name = 'hndl_classification'
    imgsz = 128
    target_detections = {PartDetectionOutModel.CLASS_HNDL}

    ordered_class_list = [
        'with_hole',
        '82081M72R53-0PG',
        'with_switch',
        '82820M75JB0-WAA',

    ]

    class_names = {k: 'HNDL' for k in ordered_class_list}
    class_colors = {k: color_green for k in ordered_class_list}


# with_hole
# ['82810M79M02-WBE', '82810M72R20-WB3', '82810M72R00-5PK']
# with_hole_switch
# ['82081M72R53-0PG']
# with_switch
# ['82820M79M31-WAA', '82810M79M42-0PG', '82081M72R44-0PG']
# without_hole
# ['82820M75JB0-WAA']