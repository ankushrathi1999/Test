from config.config import config
# from config.plc_db import SIG_SEND_HANDSHAKE_START, SIG_SEND_HANDSHAKE_END, SIG_SEND_RESULT

# plc_config = config['PLC']
# use_plc_mock = plc_config.getboolean('use_plc_mock')

# if use_plc_mock:
from .plc_mock import get_signal, send_signal, flush_plc_data
# else:
#     from .plc import get_signal, send_signal, flush_plc_data

def reset_plc():
    pass
    # send_signal(SIG_SEND_HANDSHAKE_START, 0)
    # send_signal(SIG_SEND_HANDSHAKE_END, 0)
    # send_signal(SIG_SEND_RESULT, 0)
