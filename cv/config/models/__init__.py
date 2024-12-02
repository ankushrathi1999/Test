from .part_detection_in_bottom import PartDetectionInBottomModel
from .part_detection_in_top import PartDetectionInTopModel
from .part_detection_out import PartDetectionOutModel

from .cap_bzl_classification import CapBzlClassificationModel
from .grns_fr_inr_classification import GrnsFrInrClassificationModel
from .hdl_sid_in_classification import HdlSidInClassificationModel
from .mirror_classification import MirrorClassificationModel
from .trim_set_classifcation import TrimSetClassificationModel

detection_models = [
    PartDetectionInBottomModel,
    PartDetectionInTopModel,
    PartDetectionOutModel,
]

classification_models = [
    CapBzlClassificationModel,
    GrnsFrInrClassificationModel,
    HdlSidInClassificationModel,
    MirrorClassificationModel,
    TrimSetClassificationModel,
]
