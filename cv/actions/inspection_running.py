import time

from utils.plc import send_signal,  get_signal
from config.plc_db import SIG_RECV_END_TRIGGER, SIG_SEND_START_TRIGGET_ACK, SIG_SEND_END_TRIGGET_ACK
from api.state import SYSTEM_STATES
from api.artifact import Artifact

def inspection_running_actions(data):
    ack = get_signal(SIG_RECV_END_TRIGGER)
    if ack is not True: # Handshake signal not received
        time.sleep(0.1)
        next_state = SYSTEM_STATES.INSPECTION_RUNNING
        data.state.update_state(next_state, force=True)
        return

    print("End trigger received.", SIG_RECV_END_TRIGGER)
    print("Sending end trigger acknowledgement", SIG_SEND_START_TRIGGET_ACK, [48], SIG_SEND_END_TRIGGET_ACK, [49])
    send_signal(SIG_SEND_START_TRIGGET_ACK, [48]) # Reset to 0
    send_signal(SIG_SEND_END_TRIGGET_ACK, [49]) # Set to 1

    next_state = SYSTEM_STATES.INSPECTION_END
    data.state.update_state(next_state)
