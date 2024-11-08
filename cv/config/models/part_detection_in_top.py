from ..colors import color_white, color_green

class PartDetectionInTopModel:
    name = 'part_detection_in_top'
    imgsz = 640
    target_cams = {'RH_IN_TOP', 'LH_IN_TOP'}
    tracking = False

    CLASS_BOLT_OPEN = name + '__BOLT_OPEN'
    CLASS_CAP_BZL = name + '__CAP_BZL'
    CLASS_CLIP = name + '__CLIP'
    CLASS_GLASS = name + '__GLASS'
    CLASS_GRNS_FR_INR = name + '__GRNS_FR_INR'
    CLASS_HDL_SID_IN = name + '__HDL_SID_IN'
    CLASS_LABEL = name + '__LABEL'
    CLASS_STOP_OPEN = name + '__STOP_OPEN'
    CLASS_TRIM_SET = name + '__TRIM_SET'

    ordered_class_list = [
        CLASS_BOLT_OPEN,
        CLASS_CAP_BZL,
        CLASS_CLIP,
        CLASS_GLASS,
        CLASS_GRNS_FR_INR,
        CLASS_HDL_SID_IN,
        CLASS_LABEL,
        CLASS_STOP_OPEN,
        CLASS_TRIM_SET,
    ]

    class_names = {
        CLASS_BOLT_OPEN: 'BOLT_OPEN',
        CLASS_CAP_BZL: 'CAP_BZL',
        CLASS_CLIP: 'CLIP',
        CLASS_GLASS: 'GLASS',
        CLASS_GRNS_FR_INR: 'GRNS_FR_INR',
        CLASS_HDL_SID_IN: 'HDL_SID_IN',
        CLASS_LABEL: 'LABEL',
        CLASS_STOP_OPEN: 'STOP_OPEN',
        CLASS_TRIM_SET: 'TRIM_SET',
    }

    class_confidence = {k: 0.25 for k in class_names.keys()}

    class_colors = {k: color_green for k in class_names.keys()}

    class_cams = {k:  {'RH_IN_TOP', 'LH_IN_TOP'} for k in class_names.keys()}