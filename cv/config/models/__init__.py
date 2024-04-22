from . import labels_top_cam
from . import labels_bottom_cam

class _Config:
    def __init__(self, class_names, class_confidence=None, class_colors=None, imgsz=640):
        self.class_names = class_names
        self.class_confidence = class_confidence
        self.class_colors = class_colors
        self.imgsz = imgsz

class ModelConfig:
    top_cam = _Config(
        labels_top_cam.class_names,
        class_colors=labels_top_cam.class_colors,
        class_confidence=labels_top_cam.class_confidence,
        imgsz=640
    )
    bottom_cam = _Config(
        labels_bottom_cam.class_names,
        class_colors=labels_bottom_cam.class_colors,
        class_confidence=labels_bottom_cam.class_confidence,
        imgsz=640
    )