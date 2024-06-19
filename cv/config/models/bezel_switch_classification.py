from .bezel_group_detection import BezelGroupDetectionModel
from ..colors import color_green

class BezelSwitchClassificationModel:
    name = 'bezel_switch_classification'
    imgsz = 32
    target_detections = {BezelGroupDetectionModel.CLASS_SWITCH}

    CLASS_AUTOSTART = 'autostart'
    CLASS_AUTOSTART_FLIP = 'autostart_flip'
    CLASS_CAMERA = 'camera'
    CLASS_CAMERA_FLIP = 'camera_flip'
    CLASS_DUMMY = 'dummy'
    CLASS_FOG = 'fog'
    CLASS_FOG_FLIP = 'fog_flip'
    CLASS_FUEL = 'fuel'
    CLASS_FUEL_FLIP = 'fuel_flip'
    CLASS_HEAD_LAMP = 'head_lamp'
    CLASS_HEAD_LAMP_FLIP = 'head_lamp_flip'
    CLASS_MISSING = 'missing'
    CLASS_PARK = 'park'
    CLASS_PARK_FLIP = 'park_flip'
    CLASS_TRACTION = 'traction'
    CLASS_TRACTION_FLIP = 'traction_flip'

    ordered_class_list = [
        CLASS_AUTOSTART,
        CLASS_AUTOSTART_FLIP,
        CLASS_CAMERA,
        CLASS_CAMERA_FLIP,
        CLASS_DUMMY,
        CLASS_FOG,
        CLASS_FOG_FLIP,
        CLASS_FUEL,
        CLASS_FUEL_FLIP,
        CLASS_HEAD_LAMP,
        CLASS_HEAD_LAMP_FLIP,
        CLASS_MISSING,
        CLASS_PARK,
        CLASS_PARK_FLIP,
        CLASS_TRACTION,
        CLASS_TRACTION_FLIP,
    ]

    class_names = {
        CLASS_AUTOSTART: 'ID STOP OFF, SW',
        CLASS_AUTOSTART_FLIP: 'ID STOP OFF, SW',
        CLASS_CAMERA: 'CAMERA, SW',
        CLASS_CAMERA_FLIP: 'CAMERA, SW',
        CLASS_DUMMY: 'CAP HOLE, SW',
        CLASS_FOG: 'FRONT FOG, SW',
        CLASS_FOG_FLIP: 'FRONT FOG, SW',
        CLASS_FUEL: 'FUEL, SW',
        CLASS_FUEL_FLIP: 'FUEL, SW',
        CLASS_HEAD_LAMP: 'HEAD LAMP, SW',
        CLASS_HEAD_LAMP_FLIP: 'HEAD LAMP, SW',
        CLASS_MISSING: 'MISSING, SW',
        CLASS_PARK: 'PARK SNSR, SW',
        CLASS_PARK_FLIP: 'PARK SNSR, SW',
        CLASS_TRACTION: 'ESP OFF, SW',
        CLASS_TRACTION_FLIP: 'ESP OFF, SW',
    }

    class_colors = {
        CLASS_AUTOSTART: color_green,
        CLASS_AUTOSTART_FLIP: color_green,
        CLASS_CAMERA: color_green,
        CLASS_CAMERA_FLIP: color_green,
        CLASS_DUMMY: color_green,
        CLASS_FOG: color_green,
        CLASS_FOG_FLIP: color_green,
        CLASS_FUEL: color_green,
        CLASS_FUEL_FLIP: color_green,
        CLASS_HEAD_LAMP: color_green,
        CLASS_HEAD_LAMP_FLIP: color_green,
        CLASS_MISSING: color_green,
        CLASS_PARK: color_green,
        CLASS_PARK_FLIP: color_green,
        CLASS_TRACTION: color_green,
        CLASS_TRACTION_FLIP: color_green,
    }

    yhbc_class_part_map = {
        CLASS_AUTOSTART: '37780M66R00',
        CLASS_CAMERA: '37700M66R00',
        CLASS_DUMMY: '37285M66R00',
        CLASS_FUEL: '37960M66R00',
        CLASS_HEAD_LAMP: '35180M66R00',
        CLASS_PARK: '37775M66R00',
        CLASS_TRACTION: '37585M66R00',
    }

    yl1_class_part_map = {
        CLASS_AUTOSTART: '37780M68P00',
        CLASS_DUMMY: '37285M75J00',
        CLASS_FOG: '37270M68P00',
        CLASS_HEAD_LAMP: '35180M68P00',
        CLASS_PARK: '37775M68P00',
        CLASS_TRACTION: '37585M68P10',
    }

    yxa_class_part_map = {
        CLASS_AUTOSTART: '37780M81R00',
        CLASS_CAMERA: '37700M81R00',
        CLASS_DUMMY: '37285M81R00',
        CLASS_HEAD_LAMP: '35180M69R00',
        CLASS_TRACTION: '37585M81R00',
    }

    @staticmethod
    def get_part_number(class_name, vehicle_model):
        vehicle_category = vehicle_model[:3].lower() if vehicle_model else None
        is_flip = class_name.endswith('_flip')
        if is_flip:
            class_name = class_name.replace('_flip', '')

        part_number = None
        if class_name == BezelSwitchClassificationModel.CLASS_MISSING:
            part_number = BezelSwitchClassificationModel.CLASS_MISSING
        elif vehicle_category in {'yhb', 'yhc'}:
            part_number = BezelSwitchClassificationModel.yhbc_class_part_map.get(class_name)
        elif vehicle_category in {'yl1'}:
            part_number = BezelSwitchClassificationModel.yl1_class_part_map.get(class_name)
        elif vehicle_category in {'yxa'}:
            part_number = BezelSwitchClassificationModel.yxa_class_part_map.get(class_name)

        return part_number, is_flip