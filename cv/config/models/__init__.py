from .part_detection_in_bottom import PartDetectionInBottomModel
from .part_detection_in_top import PartDetectionInTopModel
from .part_detection_out import PartDetectionOutModel

from .cap_bzl_classification import CapBzlClassificationModel
from .grns_fr_inr_classification import GrnsFrInrClassificationModel
from .hdl_sid_in_classification import HdlSidInClassificationModel
from .mirror_classification import MirrorClassificationModel
from .trim_set_classification import TrimSetClassificationModel
from .clip_tr_classification import ClipTrClassificationModel
from .hndl_classification import HndlClassificationModel
from .stop_open_classification import StopOpenClassificationModel
from .plg_fr_hole_classification import PlgFrHoleClassificationModel
from .bolt_open_classification import BoltOpenClassificationModel
from .cap_fr_out_classification import CapFrOutClassificationModel
from .wthr_fr_out_classification import WthrOutClassificationModel
from .wthr_fr_open_classification import WthrFrOutClassificationModel
from .scrw_classification import ScrwClassificationModel
from .color_classification import ColorClassificationModel


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
    ClipTrClassificationModel,
    HndlClassificationModel,
    StopOpenClassificationModel,
    PlgFrHoleClassificationModel,
    BoltOpenClassificationModel,
    CapFrOutClassificationModel,
    WthrOutClassificationModel,
    WthrFrOutClassificationModel,
    ScrwClassificationModel,
    ColorClassificationModel,
]
