from config.config import config

plc_config = config['PLC']
use_plc_mock = plc_config.getboolean('use_plc_mock')

if use_plc_mock:
    from .plc_mock import get_signal, send_signal, flush_plc_data, get_data_block
else:
    from .plc import get_signal, send_signal, flush_plc_data, get_data_block


