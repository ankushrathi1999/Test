import json

from config.plc_db import PLC_SIGNAL_LOOKUP

mock_db_path = "./data/plc_db_mock.json"
plc_data = {}
plc_data_updates = []

enable_write = False

def flush_plc_data():
    global plc_data
    with open(mock_db_path, 'r') as x:
        plc_data = json.load(x)
    
    # Updates
    if len(plc_data_updates) == 0:
        return
    while len(plc_data_updates) > 0:
        signal_name, value = plc_data_updates.pop(0)
        #print("flushing", signal_name, value)
        plc_data[signal_name] = value
    if enable_write:
        with open(mock_db_path, 'w') as x:
            json.dump(plc_data, x)
    

def get_signal(signal_name):
    return plc_data.get(signal_name)


def send_signal(signal_name, value):
    plc_data_updates.append([signal_name, value])
