from .bezel_group_detection import BezelGroupDetectionModel
from .bezel_classification import BezelClassificationModel
from .bezel_switch_classification import BezelSwitchClassificationModel

detection_models = [
    BezelGroupDetectionModel
]

classification_models = [
    BezelClassificationModel,
    BezelSwitchClassificationModel,
]