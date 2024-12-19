import configparser
import pathlib
import os
import json
import yaml
import threading

config_directory = pathlib.Path(__file__).parent.resolve()
config_files = [
    os.path.join(config_directory, 'app.config'),
    os.path.join(config_directory, 'app.priv.config'),
]

config = configparser.ConfigParser()
config.read(config_files)

# Other config files

_vehicle_parts_lookup_lh = {}
_vehicle_parts_lookup_rh = {}
_vehicle_parts_lookup_lock_lh = threading.Lock()
_vehicle_parts_lookup_lock_rh = threading.Lock()

def load_vehicle_parts_lookup():
    global _vehicle_parts_lookup_lh
    with _vehicle_parts_lookup_lock_lh:
        with open('./config/vehicle_parts_lh.yaml') as x:
            _vehicle_parts_lookup_lh = yaml.safe_load(x)
    global _vehicle_parts_lookup_rh
    with _vehicle_parts_lookup_lock_rh:
        with open('./config/vehicle_parts_rh.yaml') as x:
            _vehicle_parts_lookup_rh = yaml.safe_load(x)

def save_vehicle_parts_lookup_lh(vehicle_parts_lookup_lh):
    global _vehicle_parts_lookup_lh
    with _vehicle_parts_lookup_lock_lh:
        with open('./config/vehicle_parts_lh.yaml', 'w') as x:
            yaml.safe_dump(vehicle_parts_lookup_lh, x)
        _vehicle_parts_lookup_lh = vehicle_parts_lookup_lh

def save_vehicle_parts_lookup_rh(vehicle_parts_lookup_rh):
    global _vehicle_parts_lookup_rh
    with _vehicle_parts_lookup_lock_rh:
        with open('./config/vehicle_parts_rh.yaml', 'w') as x:
            yaml.safe_dump(vehicle_parts_lookup_rh, x)
        _vehicle_parts_lookup_rh = vehicle_parts_lookup_rh

def get_vehicle_parts_lookup_lh():
    with _vehicle_parts_lookup_lock_lh:
        return _vehicle_parts_lookup_lh
    
def get_vehicle_parts_lookup_rh():
    with _vehicle_parts_lookup_lock_rh:
        return _vehicle_parts_lookup_rh
    
def get_artificats():
    with open('./config/artifacts.yaml') as x:
        artifacts = yaml.safe_load(x)
        return artifacts

with open('./config/part_order_plc.csv') as f:
    part_order_plc = [x.strip() for x in f]

with open('./config/part_group_names.json') as x:
    part_group_names_lookup = json.load(x)