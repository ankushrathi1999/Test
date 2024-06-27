from api.state import SYSTEM_STATES
from utils.plc import send_signal
from config.plc_db import SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2

def inspection_end_actions(data):
    # Send data to PLC and save
    if data.artifact is not None:
        data.artifact.end_inspection()
        result1, result2 = data.artifact.get_part_results_plc()
        send_signal(SIG_SEND_RESULT_MID1, result1)
        send_signal(SIG_SEND_RESULT_MID2, result2)
        data.artifact.save()

    # Inspection is active after at least one cycle is completed
    data.is_active = True

    # Reset Cycle
    data.artifact = None
    next_state = SYSTEM_STATES.INSPECTION_START_PRE
    data.state.update_state(next_state)
