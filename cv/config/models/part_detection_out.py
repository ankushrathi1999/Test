from ..colors import color_white, color_green

class PartDetectionOutModel:
    name = 'part_detection_out'
    imgsz = 640
    target_cams = {'RH_OUT', 'LH_OUT'}
    tracking = False

    CLASS_HNDL = name + '__HNDL'
    CLASS_MIRROR = name + '__MIRROR'
    CLASS_WTHR_OUT = name + '__WTHR_OUT'

    ordered_class_list = [
        CLASS_HNDL,
        CLASS_MIRROR,
        CLASS_WTHR_OUT,
    ]

    class_names = {
        CLASS_HNDL: 'HNDL',
        CLASS_MIRROR: 'MIRROR',
        CLASS_WTHR_OUT: 'WTHR_OUT',
    }

    class_confidence = {k: 0.25 for k in class_names.keys()}

    class_colors = {k: color_green for k in class_names.keys()}

    class_cams = {k:  {'RH_OUT', 'LH_OUT'} for k in class_names.keys()}