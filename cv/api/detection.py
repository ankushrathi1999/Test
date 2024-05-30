class DetectionResult:
    OK = 1
    INCORRECT_PART = 0
    MISSING = 2
    FLIP = 3
    INCORRECT_POSITION = 4
    NOT_EVALUATED = 5


class ClassificationDetails:

    def __init__(self, class_id, class_name, part_number, is_flip, model, confidence, color):
        self.class_id = class_id
        self.class_name = class_name
        self.part_number = part_number
        self.is_flip = is_flip
        self.model = model
        self.confidence = confidence
        self.color = color

class FinalDetails:

    def __init__(self, label, color, result):
        self.label = label
        self.color = color
        self.result = result
        self.ignore = False

class DetectionDetails:

    def __init__(self, class_id, class_name,  model, confidence, color, bbox, cam_type):
        self.class_id = class_id
        self.class_name = class_name
        self.model = model
        self.confidence = confidence
        self.color = color
        self.bbox = bbox
        self.cam_type = cam_type
        self.classification_details = None
        self.final_details = None

    def to_dict(self):
        dct = {**vars(self)}
        dct['classification_details'] = vars(self.classification_details) if self.classification_details else None
        dct['final_details'] = vars(self.final_details) if self.final_details else None
        return dct