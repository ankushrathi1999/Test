import configparser
import pathlib
import os
import json
import yaml

config_directory = pathlib.Path(__file__).parent.resolve()
config_files = [
    os.path.join(config_directory, 'app.config'),
    os.path.join(config_directory, 'app.priv.config'),
]

config = configparser.ConfigParser()
config.read(config_files)

# Other config files

_vehicle_parts_lookup = {}
def load_vehicle_parts_lookup():
    global _vehicle_parts_lookup
    with open('./config/vehicle_parts.yaml') as x:
        _vehicle_parts_lookup = yaml.safe_load(x)

def get_vehicle_parts_lookup():
    return _vehicle_parts_lookup

with open('./config/part_order_plc.csv') as f:
    part_order_plc = [x.strip() for x in f]

with open('./config/part_group_names.json') as x:
    part_group_names_lookup = json.load(x)