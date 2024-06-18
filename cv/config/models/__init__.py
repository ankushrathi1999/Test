from .bezel_group_detection import BezelGroupDetectionModel
from .part_detection import PartDetectionModel
from .bezel_classification import BezelClassificationModel
from .bezel_switch_classification import BezelSwitchClassificationModel
from .usb_aux_classification import UsbAuxClassificationModel
from .part_classification import PartClassificationModel
from .sensor_classification import SensorClassificationModel

detection_models = [
    BezelGroupDetectionModel,
    PartDetectionModel,
]

classification_models = [
    BezelClassificationModel,
    BezelSwitchClassificationModel,
    UsbAuxClassificationModel,
    PartClassificationModel,
    SensorClassificationModel,
]