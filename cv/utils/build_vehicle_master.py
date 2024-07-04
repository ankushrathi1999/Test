import pymysql
import pymysql.cursors
from collections import  defaultdict
import pandas as pd
import json
import yaml

from .db import get_vehicle_models, get_vehicle_part_mapping

def _process_vehicle_type(vehicle_data, vehicle_part_type_groups, vehicle_type_upper_panel_map):
    for vehicle_model in list(vehicle_part_type_groups.keys()):
        generic_parts = vehicle_part_type_groups[vehicle_model]['generic_parts']
        for part, details in generic_parts:
            if details.part_class == 'upper_panel':
                if part['part_number'] in vehicle_type_upper_panel_map:
                    vehicle_data[vehicle_model]['vehicle_type'] = vehicle_type_upper_panel_map[part['part_number']]
                else:
                    print("Unregistered upper panel found:", part['part_number'])
                    vehicle_part_type_groups.pop(vehicle_model)
                break
        else:
            print("Upper panel is not registered for vehicle:", vehicle_model)
            vehicle_part_type_groups.pop(vehicle_model)

# todo: LHD vehicles have opposite sensor placements, currently parts are added in RHD spec only
def _add_missing_sensor_parts(vehicle_parts, part_master_lookup, missing_part_checks):
    ip_upr = [v for v in vehicle_parts if part_master_lookup.loc[v['part_number']].part_class == 'upper_panel']
    if len(ip_upr) == 0:
        return vehicle_parts
    classes = set()
    for part in vehicle_parts:
        details = part_master_lookup.loc[part['part_number']]
        classes.add(details['part_class'])
    for part in missing_part_checks:
        if part['part_class'] not in classes:
            vehicle_parts.append({
                **part,
                "is_miss": True,
            })
    return vehicle_parts

def _group_part_types(vehicle_parts, part_master_lookup):
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

def _process_generic_parts(vehicle_data, vehicle_part_type_groups, missing_class_name_lookup):
    for vehicle_model in vehicle_part_type_groups:
        generic_parts = vehicle_part_type_groups[vehicle_model]['generic_parts']
        for part, details in generic_parts:
            data = vehicle_data[vehicle_model][details.part_class] = {
                "part_name": details.part_name_msil,
                "part_number": part['part_number'],
                "part_name_long": part['part_name'],
            }
            if part.get('is_miss'):
                data['is_miss'] = True
            if len(details.part_group_name.strip()) > 0:
                data["is_group"] = True
                data["part_group"] = details.part_group_name.strip()
            missing_class_name = missing_class_name_lookup.get(details.part_class)
            if missing_class_name is not None:
                data['missing_class_name'] = missing_class_name

def _process_usb_aux_group(vehicle_data, vehicle_part_type_groups, missing_class_name_lookup):
    for vehicle_model in vehicle_part_type_groups:
        usb_aux_group = vehicle_part_type_groups[vehicle_model]['usb_aux_group']
        if len(usb_aux_group) == 0:
            print('No usb aux data for vehicle:', vehicle_model)
            continue
        assert 2 <= len(usb_aux_group) <= 3
        usb_aux_group = sorted(usb_aux_group, key=lambda x: x[0]['part_position'])
        missing_class_name = missing_class_name_lookup.get('usb_aux') # todo: hardcoded class name
        vehicle_data[vehicle_model]['usb_aux_group'] = {
            "n_parts": len(usb_aux_group),
            "parts": list(map(lambda part: {
                "part_name": part[1].part_name_msil,
                "part_number": part[0]['part_number'],
                "part_name_long": part[0]['part_name'],
                "missing_class_name": missing_class_name,
            }, usb_aux_group))
        }

def _process_bezel_group(vehicle_data, vehicle_part_type_groups, bezel_switch_positions):
    for vehicle_model in vehicle_part_type_groups:
        bezel = vehicle_part_type_groups[vehicle_model]['bezel']
        bezel_switches = vehicle_part_type_groups[vehicle_model]['bezel_switches']
        if len(bezel) != 1:
            print('No bezel data for vehicle:', vehicle_model)
            continue
        bezel_part, bezel_part_details = bezel[0]
        switch_positions_top, switch_positions_bottom = bezel_switch_positions[bezel_part['part_number']]
        data = vehicle_data[vehicle_model]['bezel'] = {
            "id": bezel_part['part_number'],
            "name": bezel_part['part_name'],
            "n_rows": 2 if len(switch_positions_bottom) > 0 else 1,
        }
        if len(bezel_switches) == 0:
            print('No switch data for vehicle:', vehicle_model)
            data['switches_top'] = [{'id': 'na', 'name': 'N/A', 'position': 1}]
            continue
        assert len(switch_positions_top) + len(switch_positions_bottom) == len(bezel_switches), (vehicle_model, len(switch_positions_top), len(switch_positions_bottom), len(bezel_switches))
        switch_pos_lookup = {}
        for part, details in bezel_switches:
            pos = part['part_position']
            assert pos not in switch_pos_lookup, (part, pos)
            switch_pos_lookup[pos] = (part, details)
        assert len(switch_positions_top) > 0, vehicle_model
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

def build_vehicle_master():
    print("Building vehicle master")

    # Part Master CSV
    part_master = pd.read_csv('./config/part_master.csv').fillna('')
    part_master_lookup = part_master.set_index('part_number')
    print("Parts loaded:", len(part_master))

    vehicle_models = get_vehicle_models()
    print("Vehicle models:", len(vehicle_models))

    mapping = get_vehicle_part_mapping(vehicle_models)
    print("Vehicle part mapping:", len(mapping))

    with open('./config/missing_class_names.json', 'r') as f:
        missing_class_name_lookup = json.load(f)
    print("Missing classes registered:", len(missing_class_name_lookup))

    with open('./config/missing_part_checks.json', 'r') as f:
        missing_part_checks = json.load(f)
    print("Missing part checks:", len(missing_part_checks))

    with open('./config/bezel_switch_positions.json', 'r') as f:
        bezel_switch_positions = json.load(f)
    print("Bezels registered for switch position:", len(bezel_switch_positions))

    with open('./config/vehicle_type_upper_panel_map.json', 'r') as f:
        vehicle_type_upper_panel_map = json.load(f)
    print("Upper panels registered:", len(vehicle_type_upper_panel_map))

    print("Count of parts by vechicle model:")
    for vehicle_model, vehicle_parts in mapping.items():
        print(vehicle_model, len(vehicle_parts))

    vehicle_part_type_groups = {vehicle_model: _group_part_types(
        _add_missing_sensor_parts(vehicle_parts, part_master_lookup, missing_part_checks),
        part_master_lookup) for vehicle_model, vehicle_parts in mapping.items()}
    vehicle_data = defaultdict(dict)
    _process_vehicle_type(vehicle_data, vehicle_part_type_groups, vehicle_type_upper_panel_map)
    _process_generic_parts(vehicle_data, vehicle_part_type_groups, missing_class_name_lookup)
    _process_usb_aux_group(vehicle_data, vehicle_part_type_groups, missing_class_name_lookup)
    _process_bezel_group(vehicle_data, vehicle_part_type_groups, bezel_switch_positions)

    yaml_path = './config/vehicle_parts.yaml'
    with open(yaml_path, 'w') as x:
        yaml.safe_dump(dict(vehicle_data), x)
    print("Vehicle master successfully written:", yaml_path)
