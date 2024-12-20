from ..colors import color_white, color_green

class PartDetectionInBottomModel:
    name = 'part_detection_in_bottom'
    imgsz = 640
    target_cams = {'RH_IN_BOTTOM', 'LH_IN_BOTTOM'}
    tracking = False

    CLASS_BOLT_OPEN = name + '__BOLT_OPEN'
    CLASS_LABEL = name + '__LABEL'
    CLASS_PLG_FR_HOLE = name + '__PLG_FR_HOLE'
    CLASS_PNT_GRMT = name + '__PNT_GRMT'
    CLASS_SCRW = name + '__SCRW'
    CLASS_TRIM_SET = name + '__TRIM_SET'
    CLASS_WTHR_FR_OPEN = name + '__WTHR_FR_OPEN'

    ordered_class_list = [
        CLASS_BOLT_OPEN,
        None, #CLASS_LABEL,
        CLASS_PLG_FR_HOLE,
        CLASS_PNT_GRMT,
        CLASS_SCRW,
        None, #CLASS_TRIM_SET,
        CLASS_WTHR_FR_OPEN,
    ]

    class_names = {
        CLASS_BOLT_OPEN: 'BOLT_OPEN',
        CLASS_LABEL: 'LABEL',
        CLASS_PLG_FR_HOLE: 'PLG_FR_HOLE',
        CLASS_PNT_GRMT: 'PNT_GRMT',
        CLASS_SCRW: 'SCRW',
        CLASS_TRIM_SET: 'TRIM_SET',
        CLASS_WTHR_FR_OPEN: 'WTHR_FR_OPEN'
    }

    class_confidence = {k: 0.25 for k in class_names.keys()}

    class_colors = {k: color_green for k in class_names.keys()}

    class_cams = {k:  {'RH_IN_BOTTOM', 'LH_IN_BOTTOM'} for k in class_names.keys()}
    
    class_cam_rois = {k: {} for k in class_names.keys()}
    class_cam_rois[CLASS_BOLT_OPEN] = {
        'RH_IN_TOP': [0, 0.60],
        'LH_IN_TOP': [0.40, 1],
    }