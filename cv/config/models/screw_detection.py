from ..colors import color_white, color_green

class ScrewDetectionModel:
    name = 'screw_detection'
    imgsz = 32
    target_cams = {'bottom'}
    tracking = True

    CLASS_SCREW_BIG = name + '_screw_big'
    CLASS_SCREW_SMALL = name + '_screw_small'

    ordered_class_list = [
        CLASS_SCREW_BIG,
        CLASS_SCREW_SMALL,
    ]

    class_names = {
        CLASS_SCREW_BIG: 'SCREW',
        CLASS_SCREW_SMALL: 'SCREW',
    }

    class_confidence = {
        CLASS_SCREW_BIG: 0.25,
        CLASS_SCREW_SMALL: 0.25,
    }

    class_colors = {
        CLASS_SCREW_BIG: color_green,
        CLASS_SCREW_SMALL: color_green,
    }

    class_cams = {
        CLASS_SCREW_BIG: target_cams,
        CLASS_SCREW_SMALL: target_cams,
    }