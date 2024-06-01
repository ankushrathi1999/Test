from .bezel_group_detection import BezelGroupDetectionModel
from .part_detection import PartDetectionModel
from .bezel_classification import BezelClassificationModel
from .bezel_switch_classification import BezelSwitchClassificationModel
from .part_classification import PartClassificationModel

detection_models = [
    BezelGroupDetectionModel,
    PartDetectionModel,
]

classification_models = [
    BezelClassificationModel,
    BezelSwitchClassificationModel,
    PartClassificationModel,
]