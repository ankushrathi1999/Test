import pymcprotocol

from config.plc_db import PLC_SIGNAL_LOOKUP
from config.config import config

plc_config = config['PLC']
ip_address = plc_config.get('ip_address')
port = plc_config.getint('port')

plc_data = None
plc_data_updates = []

def get_str(data, pos, size):
    chars = []
    for i, word in enumerate(data):
        if pos > i*2+1:
            continue
        part2 = chr(word >> 8)
        part1 = chr(word & 0xFF)
        if i*2 >= pos:
            chars.append(part1)
        if len(chars) >= size:
            break
        chars.append(part2)
        if len(chars) >= size:
            break
    return "".join(chars)

def get_int(data, pos):
    return data[pos]

def get_bool(data, pos):
    return chr(data[pos]) == "1"

def flush_plc_data():
    global plc_data

    # Create a client object
    pymc3e = pymcprotocol.Type3E(plctype="iQ-R")
    pymc3e.setaccessopt(commtype="binary")
    pymc3e.connect(ip_address, port)

    # Get data
    plc_data = pymc3e.batchread_wordunits(headdevice="D16001", readsize=20) # parameterize
    print(plc_data)

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
    pos = signal["pos"]
    size = signal.get("size")

    if signal_type == "int":
        return get_int(plc_data, pos)
    elif signal_type == "bool":
        return get_bool(plc_data, pos)
    elif signal_type == "str":
        return get_str(plc_data, pos, size)
    return None
