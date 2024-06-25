from .bezel_group_detection import BezelGroupDetectionModel
from .part_detection_v2 import PartDetectionModel
from .bezel_classification import BezelClassificationModel
from .bezel_switch_classification import BezelSwitchClassificationModel
from .usb_aux_classification import UsbAuxClassificationModel
from .part_classification_v2 import PartClassificationModel
from .sensor_classification import SensorClassificationModel
from .ac_control_classification import ACControlClassificationModel
from .lights_classification import LightsClassificationModel
from .wiper_classification import WiperClassificationModel
from .lower_panel_classification import LowerPanelClassificationModel
from .orn_classification import OrnClassificationModel

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
    ACControlClassificationModel,
    LightsClassificationModel,
    WiperClassificationModel,
    LowerPanelClassificationModel,
    OrnClassificationModel,
]