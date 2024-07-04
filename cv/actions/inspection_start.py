import time

from utils.plc import send_signal,  get_signal
from config.plc_db import (
    SIG_RECV_START_TRIGGER, SIG_RECV_PSN, SIG_RECV_MODEL, SIG_RECV_CHASSIS, SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2,
    SIG_SEND_START_TRIGGET_ACK, SIG_SEND_END_TRIGGET_ACK
)
from api.state import SYSTEM_STATES
from api.artifact import Artifact

def inspection_start_actions(data):
    print("Fetching Part data from PLC")
    ack = get_signal(SIG_RECV_START_TRIGGER)
    if ack is not True: # Handshake signal not received
        time.sleep(1)
        next_state = SYSTEM_STATES.INSPECTION_START
        data.state.update_state(next_state, force=True)
        return

    psn = get_signal(SIG_RECV_PSN)
    chassis = get_signal(SIG_RECV_CHASSIS)
    vehicle_model = get_signal(SIG_RECV_MODEL)
    print("Fetched part data:", psn, chassis, vehicle_model)

    # Reset results on PLC
    print("Sending start trigger acknowledgement", SIG_SEND_END_TRIGGET_ACK, [48], SIG_SEND_START_TRIGGET_ACK, [49])
    send_signal(SIG_SEND_END_TRIGGET_ACK, [48]) # Reset to 0
    send_signal(SIG_SEND_START_TRIGGET_ACK, [49]) # Set to 1
    reset_value = [0 for _ in range(23)]
    print("Resetting PLC results", SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2, reset_value)
    send_signal(SIG_SEND_RESULT_MID1, reset_value)
    send_signal(SIG_SEND_RESULT_MID2, reset_value)

    # Initialize engine
    if data.is_active:
        print("Initializing artifact.")
        data.artifact = Artifact(psn, chassis, vehicle_model, data)
    else:
        print("Data active flag is off. Skipping inspection.")

    next_state = SYSTEM_STATES.INSPECTION_RUNNING
    data.state.update_state(next_state)
