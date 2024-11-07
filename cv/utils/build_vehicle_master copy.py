from collections import  defaultdict
import pandas as pd
import json
import yaml
import logging

from .db import get_vehicle_models, get_vehicle_part_mapping
from config.config import save_vehicle_parts_lookup

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    pass

def process_vehicle_type(vehicle_data, vehicle_model, generic_parts, vehicle_type_upper_panel_map):
    for part, details in generic_parts:
        if details.part_class == 'upper_panel':
            if part['part_number'] in vehicle_type_upper_panel_map:
                vehicle_data['vehicle_type'] = vehicle_type_upper_panel_map[part['part_number']]
            else:
                raise ValidationError(f"Unregistered upper panel found: {part['part_number']}.")
            break
    else:
        raise ValidationError(f"Upper panel is not registered for vehicle: {vehicle_model}.")

def process_n_screws(vehicle_data, vehicle_model):
    vehicle = vehicle_model[:3]
    try:
        vehicle_data['n_screws'] = {
            'YHB': 5,
            'YED': 5,
            'YHC': 5,
            'YXA': 5,
            'YL1': 3,
            'YCA': 0,
            'YSD': 0,
        }[vehicle]
    except KeyError:
        raise ValidationError(f"Screw count is not registered for {vehicle}.")

sensor_sun_part = {
    "part_name": "SENSOR, SUN LIGHT",
    "part_number": "95642-64G20"
}
sensor_auto_part = {
    "part_name": "SENSOR, AUTO LIGHT",
    "part_number": "38680M56R00"
}
sensor_vehicle_exclusions = {'YCA'}

def add_missing_sensor_parts(vehicle_model, vehicle_parts, part_master_lookup, vehicle_type_upper_panel_map):
    ip_upr = [v for v in vehicle_parts if part_master_lookup.loc[v['part_number']].part_class == 'upper_panel']
    if len(ip_upr) == 0:
        return vehicle_parts
    vehicle = vehicle_model[:3]
    if vehicle in sensor_vehicle_exclusions:
        return vehicle_parts
    try:
        assert len(ip_upr) == 1, f"Multiple upper panels registered: {vehicle_model} ({len(ip_upr)})"
    except AssertionError as ex:
        logger.warn(str(ex))
        return vehicle_parts
    vtype = vehicle_type_upper_panel_map[ip_upr[0]['part_number']]
    sensor_sun = None
    sensor_auto = None
    for part in vehicle_parts:
        details = part_master_lookup.loc[part['part_number']]
        if details['part_class'] == 'sensor_sun':
            sensor_sun = part
        elif details['part_class'] == 'sensor_auto':
            sensor_auto = part
    sensor_sun_class = "sensor_right" if vtype == 'RHD' else "sensor_left"
    sensor_auto_class = "sensor_left" if vtype == 'RHD' else "sensor_right"
    if sensor_sun is None:
        vehicle_parts.append({
            **sensor_sun_part,
            "part_class": sensor_sun_class,
            "is_miss": True,
        })
    else:
        sensor_sun["part_class"] = sensor_sun_class
    if sensor_auto is None:
        vehicle_parts.append({
            **sensor_auto_part,
            "part_class": sensor_auto_class,
            "is_miss": True,
        })
    else:
        sensor_auto["part_class"] = sensor_auto_class
    return vehicle_parts

def group_part_types(vehicle_parts, part_master_lookup):
    bezel = []
    bezel_switches = []
    usb_aux_group = []
    generic_parts = []
    for part in vehicle_parts:
        details = part_master_lookup.loc[part['part_number']]
        {
            'bezel': bezel,
            'bezel_switch': bezel_switches,
            'usb_aux': usb_aux_group,
        }.get(details['part_class'], generic_parts).append([part, details])
    return {
        'bezel': bezel,
        'bezel_switches': bezel_switches,
        'usb_aux_group': usb_aux_group,
        'generic_parts': generic_parts
    }

def process_generic_parts(vehicle_data, generic_parts, missing_class_name_lookup):
    for part, details in generic_parts:
        if details['is_supported'] == 0:
            continue
        part_class = part.get('part_class', details.part_class)
        data = vehicle_data[part_class] = {
            "part_name": details.part_name_msil,
            "part_number": part['part_number'],
            "part_name_long": part['part_name'],
        }
        if part.get('is_miss'):
            data['is_miss'] = True
        if len(details.part_group_name.strip()) > 0:
            data["is_group"] = True
            data["part_group"] = details.part_group_name.strip()
        missing_class_name = missing_class_name_lookup.get(part_class)
        if missing_class_name is not None:
            data['missing_class_name'] = missing_class_name

def process_usb_aux_group(vehicle_data, vehicle_model, usb_aux_group, missing_class_name_lookup):
    if len(usb_aux_group) == 0:
        raise ValidationError(f'No USB or ACC switches have been added for {vehicle_model}.')
    if not (1 <= len(usb_aux_group) <= 3):
        raise ValidationError(f'Invalid count of USB and ACC switches for {vehicle_model}. Expected: 1 to 3. Got: {len(usb_aux_group)}.')
    usb_aux_group = sorted(usb_aux_group, key=lambda x: (x[0]['part_position'] or 0))
    missing_class_name = missing_class_name_lookup.get('usb_aux') # todo: hardcoded class name
    vehicle_data['usb_aux_group'] = {
        "n_parts": len(usb_aux_group),
        "parts": list(map(lambda part: {
            "part_name": part[1].part_name_msil,
            "part_number": part[0]['part_number'],
            "part_name_long": part[0]['part_name'],
            "missing_class_name": missing_class_name,
        }, usb_aux_group))
    }

def process_bezel_group(vehicle_data, vehicle_model, bezel, bezel_switches, bezel_switch_positions):
    if len(bezel) == 0:
        vehicle = vehicle_model[:3]
        if vehicle not in bezel_switch_positions:
            raise ValidationError(f"Bezel part has not been added for {vehicle_model}.")
        switch_positions_top, switch_positions_bottom = bezel_switch_positions[vehicle]
        data = vehicle_data['bezel'] = {
            "id": "na",
            "name": "na",
            "n_rows": 2 if len(switch_positions_bottom) > 0 else 1,
        }
    elif len(bezel) > 1:
        raise ValidationError(f"Multiple bezel parts have been added for {vehicle_model}. Expecting exactly 1.")
    else:
        bezel_part, bezel_part_details = bezel[0]
        if bezel_part['part_number'] not in bezel_switch_positions:
            raise ValidationError(f"Bezel part {bezel_part['part_number']} is not registered.")
        switch_positions_top, switch_positions_bottom = bezel_switch_positions[bezel_part['part_number']]
        data = vehicle_data['bezel'] = {
            "id": "na" if bezel_part_details['is_supported'] == 0 else bezel_part['part_number'],
            "name": bezel_part['part_name'],
            "n_rows": 2 if len(switch_positions_bottom) > 0 else 1,
        }

    if len(bezel_switches) == 0:
        data['switches_top'] = [{'id': 'na', 'name': 'N/A', 'position': 1}]
        raise ValidationError(f'No bezel switches have been added for {vehicle_model}.')

    _expected = len(switch_positions_top) + len(switch_positions_bottom)
    _actual = len(bezel_switches) 
    if _expected != _actual:
        data['switches_top'] = [{'id': 'na', 'name': 'N/A', 'position': 1}]
        raise ValidationError(f"Incorrect number of bezel switches have been added. Expected: {_expected}, Got: {_actual}.")

    switch_pos_lookup = {}
    _actual_pos = set()
    for part, details in bezel_switches:
        pos = part['part_position']
        if pos in _actual_pos:
            raise ValidationError(f"Multple bezel switches have been added at position {pos}.")
        _actual_pos.add(int(pos))
        switch_pos_lookup[pos] = (part, details)
    _expected_pos = set()
    for pos in switch_positions_top:
        _expected_pos.add(int(pos))
    for pos in switch_positions_bottom:
        _expected_pos.add(int(pos))
    _extra_pos = _actual_pos - _expected_pos
    if len(_extra_pos) > 0:
        raise ValidationError(f"Invalid bezel switch positions have been identified: {sorted(_extra_pos)}. Valid positions are: {sorted(_expected_pos)}.")
    _missing_pos =  _expected_pos - _actual_pos
    if len(_missing_pos) > 0:
        raise ValidationError(f"The following bezel switch positions have not been specified: {sorted(_missing_pos)}. Valid positions are: {sorted(_expected_pos)}.")

    data['switches_top'] = []
    for pos in switch_positions_top:
        part, details = switch_pos_lookup[str(pos)]
        data['switches_top'].append({
            'id': part['part_number'],
            'name': part['part_name'],
            'position': int(part['part_position']),
        })
    if len(switch_positions_bottom) > 0:
        data['switches_bottom'] = []
        for pos in switch_positions_bottom:
            part, details = switch_pos_lookup[str(pos)]
            data['switches_bottom'].append({
                'id': part['part_number'],
                'name': part['part_name'],
                'position': int(part['part_position']),
            })

def prepare_vehicle_master(vehicle_model, metadata):
    (vehicle_part_type_groups, missing_class_name_lookup, bezel_switch_positions, vehicle_type_upper_panel_map) = metadata
    
    errors = []
    vehicle_data = {}

    if vehicle_model not in vehicle_part_type_groups:
        errors.append(f"No parts have been registered for {vehicle_model}.")
        return None, errors
    vehicle_part_type_groups = vehicle_part_type_groups[vehicle_model]

    try:
        process_n_screws(vehicle_data, vehicle_model)
    except ValidationError as ex:
        errors.append(str(ex))
    
    process_generic_parts(vehicle_data, vehicle_part_type_groups['generic_parts'], missing_class_name_lookup)

    try:
        process_usb_aux_group(vehicle_data, vehicle_model, vehicle_part_type_groups['usb_aux_group'], missing_class_name_lookup)
    except ValidationError as ex:
        errors.append(str(ex))

    try:
        process_bezel_group(vehicle_data, vehicle_model, vehicle_part_type_groups['bezel'],
                            vehicle_part_type_groups['bezel_switches'], bezel_switch_positions)
    except ValidationError as ex:
        errors.append(str(ex))

    try:
        process_vehicle_type(vehicle_data, vehicle_model, vehicle_part_type_groups['generic_parts'], vehicle_type_upper_panel_map)
    except ValidationError as ex:
        errors.append(str(ex))
        return None, errors

    return vehicle_data, errors

    
def get_metadata(vehicle_models, keep_inactive_parts=False):
    # Part Master CSV
    part_master = pd.read_csv('./config/part_master.csv').fillna('')
    part_master_lookup = part_master.set_index('part_number')
    logger.debug("Parts loaded: %s", len(part_master))

    mapping = get_vehicle_part_mapping(vehicle_models, keep_inactive_parts=keep_inactive_parts)
    logger.debug("Vehicle part mapping: %s", len(mapping))

    with open('./config/missing_class_names.json', 'r') as f:
        missing_class_name_lookup = json.load(f)
    logger.debug("Missing classes registered: %s", len(missing_class_name_lookup))

    with open('./config/bezel_switch_positions.json', 'r') as f:
        bezel_switch_positions = json.load(f)
    logger.debug("Bezels registered for switch position: %s", len(bezel_switch_positions))

    with open('./config/vehicle_type_upper_panel_map.json', 'r') as f:
        vehicle_type_upper_panel_map = json.load(f)
    logger.debug("Upper panels registered: %s", len(vehicle_type_upper_panel_map))

    logger.debug("Count of parts by vechicle model:")
    for vehicle_model, vehicle_parts in mapping.items():
        logger.debug("%s=%s", vehicle_model, len(vehicle_parts))

    vehicle_part_type_groups = {vehicle_model: group_part_types(
        add_missing_sensor_parts(vehicle_model, vehicle_parts, part_master_lookup, vehicle_type_upper_panel_map),
        part_master_lookup) for vehicle_model, vehicle_parts in mapping.items()}
    
    return vehicle_part_type_groups, missing_class_name_lookup, bezel_switch_positions, vehicle_type_upper_panel_map


def validate_vehicle_part_data(vehicle_model):
    metadata = get_metadata([vehicle_model], keep_inactive_parts=True)
    try:
        data, errors = prepare_vehicle_master(vehicle_model, metadata)
        is_valid = len(errors) == 0
    except Exception as ex:
        message = f"Failed to validate parts data for {vehicle_model}. [INTERNAL ERROR]."
        logger.exception(message)
        errors = [message]
        is_valid = False
    return is_valid, errors


def build_all_vehicle_master():
    logger.debug("Building vehicle master")
    
    vehicle_models = get_vehicle_models()
    logger.debug("Vehicle models: %s", len(vehicle_models))

    metadata = get_metadata(vehicle_models)
    
    vehicle_data = defaultdict(dict)
    for vehicle_model in vehicle_models:
        try:
            data, errors = prepare_vehicle_master(vehicle_model, metadata)
            if len(errors) > 0:
                logger.error("Validation errors for %s", vehicle_model)
                for err in errors:
                    logger.error(str(err))
            if data is not None:
                vehicle_data[vehicle_model] = data
        except Exception as ex:
            logger.exception("Error processing %s. %s", vehicle_model, ex)

    if len(vehicle_data) > 0:
        save_vehicle_parts_lookup(dict(vehicle_data))
        logger.debug("Vehicle master successfully written")
    else:
        logger.error("No vehicles were successfully processed.")