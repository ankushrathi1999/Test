import time

from utils.plc import send_signal,  get_signal
from config.plc_db import SIG_RECV_END_TRIGGER, SIG_RECV_PSN, SIG_RECV_MODEL, SIG_RECV_CHASSIS
from api.state import SYSTEM_STATES
from api.artifact import Artifact

def inspection_running_actions(data):
    ack = get_signal(SIG_RECV_END_TRIGGER)
    if ack is not True: # Handshake signal not received
        time.sleep(0.1)
        next_state = SYSTEM_STATES.INSPECTION_RUNNING
        data.state.update_state(next_state, force=True)
        return

    print("End trigger received.")
    next_state = SYSTEM_STATES.INSPECTION_END
    data.state.update_state(next_state)
