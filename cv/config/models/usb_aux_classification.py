from .part_detection import PartDetectionModel
from ..colors import color_white, color_green

class UsbAuxClassificationModel:
    name = 'usb_aux_classification'
    imgsz = 64
    target_detections = {PartDetectionModel.CLASS_usb_aux}

    ordered_class_list = [
        '39440M56R20-5PK',
        '39441M75J01-5PK',
        '88411M76T00',
        '95525M72S00',
        '39105M77S00-5PK',
        '37275M75J00',
        '39105M56R00-5PK',
    ]

    class_names = {
        '39440M56R20-5PK': 'ACC_SKT',
        '39441M75J01-5PK': 'ACC_SKT',
        '88411M76T00': 'SW_ST_VNT',
        '95525M72S00': 'SW_ST_VNT',
        '39105M77S00-5PK': 'USB_SKT',
        '37275M75J00': 'USB_SKT',
        '39105M56R00-5PK': 'USB_SKT',
    }

    class_colors = {
        '39440M56R20-5PK': color_green,
        '39441M75J01-5PK': color_green,
        '88411M76T00': color_green,
        '95525M72S00': color_green,
        '39105M77S00-5PK': color_green,
        '37275M75J00': color_green,
        '39105M56R00-5PK': color_green,
    }