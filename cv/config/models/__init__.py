from .bezel_group_detection import BezelGroupDetectionModel
from .part_detection_v2 import PartDetectionModel
from .screw_detection import ScrewDetectionModel
from .bezel_classification import BezelClassificationModel
from .bezel_switch_classification import BezelSwitchClassificationModel
from .usb_aux_classification import UsbAuxClassificationModel
from .part_classification_v2 import PartClassificationModel
from .sensor_classification import SensorClassificationModel
from .ac_control_classification import ACControlClassificationModel
from .lights_wiper_classification import LightsWiperClassificationModel
from .lower_panel_classification import LowerPanelClassificationModel
from .orn_classification import OrnClassificationModel
from .gar_ct_classification import GarCTClassificationModel

detection_models = [
    BezelGroupDetectionModel,
    PartDetectionModel,
    ScrewDetectionModel,
]

classification_models = [
    BezelClassificationModel,
    BezelSwitchClassificationModel,
    UsbAuxClassificationModel,
    PartClassificationModel,
    SensorClassificationModel,
    ACControlClassificationModel,
    LightsWiperClassificationModel,
    LowerPanelClassificationModel,
    OrnClassificationModel,
    GarCTClassificationModel,
]