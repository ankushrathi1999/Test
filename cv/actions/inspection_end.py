from api.state import SYSTEM_STATES
from utils.plc import send_signal
from config.plc_db import SIG_SEND_RESULT

def inspection_end_actions(data):
    # Send data to PLC and save
    data.artifact.end_inspection()
    send_signal(SIG_SEND_RESULT, data.artifact.get_part_results_plc())
    data.artifact.save()

    # Reset Cycle
    data.artifact = None
    next_state = SYSTEM_STATES.INSPECTION_START_PRE
    data.state.update_state(next_state)
