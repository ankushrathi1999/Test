import pymcprotocol

from config.plc_db import PLC_SIGNAL_LOOKUP
from config.config import config

plc_config = config['PLC']
ip_address = plc_config.get('ip_address')
port = plc_config.get('port')

plc_data = None
plc_data_updates = []

def get_int(data, start_byte):
    return int(data[start_byte])

def set_int(data, start_byte, value):
    # todo: data[start_byte] = byte(value)
    pass

def get_str(data, start_byte, size):
    # todo: str(data[start_byte: start_byte+size])
    return ""

def flush_plc_data():
    global plc_data

    # Create a client object
    pymc3e = pymcprotocol.Type3E(plctype="iQ-R")
    pymc3e.setaccessopt(commtype="binary")
    pymc3e.connect(ip_address, port)

    # Get data
    plc_data = pymc3e.batchread_wordunits(headdevice="D100", readsize=50)

    # Updates
    # if len(plc_data_updates) == 0:
    #     return
    # while len(plc_data_updates) > 0:
    #     signal_name, value = plc_data_updates.pop(0)
    #     signal = PLC_SIGNAL_LOOKUP[signal_name]
    #     signal_type = signal["type"]
    #     start_byte = signal["startByte"]
    #     size = signal["size"]
    #     if signal_type == "int":
    #         set_int(plc_data, start_byte, value)
    #     else:
    #         raise Exception(f"Unsupported data type for write: {signal_type}")
    # pymc3e.batchwrite_wordunits(headdevice="D100", values=plc_data)


def send_signal(signal_name, value):
    plc_data_updates.append([signal_name, value])

def get_signal(signal_name):
    if plc_data is None:
        return None
    
    signal = PLC_SIGNAL_LOOKUP[signal_name]
    signal_type = signal["type"]
    start_byte = signal["startByte"]
    size = signal["size"]

    if signal_type == "int":
        return get_int(plc_data, start_byte)
    elif signal_type == "str":
        return get_str(plc_data, start_byte, size)
    return None
