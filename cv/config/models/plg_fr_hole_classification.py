from .part_detection_in_bottom import PartDetectionInBottomModel
from ..colors import color_green, color_red

class PlgFrHoleClassificationModel:
    name = 'plg_fr_hole_classification'
    imgsz = 32
    target_detections = {PartDetectionInBottomModel.CLASS_PLG_FR_HOLE}

    ordered_class_list = [
        'NG_plg_fr_hole',
        '09250M25L01',
    ]

    class_names = {k: 'PLG_FR_HOLE' for k in ordered_class_list}
    class_names['NG_plg_fr_hole'] = 'NG_PLG_FR_HOLE'
    class_colors = {k: color_green for k in ordered_class_list}
    class_colors['NG_plg_fr_hole'] = color_red
