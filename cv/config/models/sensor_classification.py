from .part_detection import PartDetectionModel
from ..colors import color_white, color_green, color_red

class SensorClassificationModel:
    name = 'sensor_classification'
    imgsz = 32
    target_detections = {PartDetectionModel.CLASS_sensor_left, PartDetectionModel.CLASS_sensor_right}

    ordered_class_list = [
        '38680M56R00', # Auto Sensor
        'no_sensor', # No Sensor
        '95642-64G20', # Sun Sensor
    ]

    class_names = {
        '38680M56R00': 'SNSR_AUTO',
        'no_sensor': 'SNSR_MISS',
        '95642-64G20': 'SNSR_SUN',
    }

    class_colors = {
        '38680M56R00': color_green,
        'no_sensor': color_red,
        '95642-64G20': color_green,
    }