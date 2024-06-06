from ..colors import color_white, color_green

class BezelGroupDetectionModel:
    name = 'bezel_group_detection'
    imgsz = 640
    target_cams = {'top', 'bottom'}

    CLASS_SWITCH = name + '_switch'
    CLASS_CONTAINER = name + '_container'

    ordered_class_list = [
        CLASS_CONTAINER,
        CLASS_SWITCH,
    ]

    class_names = {
        CLASS_SWITCH: 'Bezel Switch',
        CLASS_CONTAINER: 'Bezel Container',
    }

    class_confidence = {
        CLASS_SWITCH: 0.25,
        CLASS_CONTAINER: 0.25,
    }

    class_colors = {
        CLASS_SWITCH: color_green,
        CLASS_CONTAINER: color_green,
    }

    class_cams = {
        CLASS_SWITCH: target_cams,
        CLASS_CONTAINER: target_cams,
    }