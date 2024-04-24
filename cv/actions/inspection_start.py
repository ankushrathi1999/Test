import time

from utils.plc import send_signal,  get_signal
from config.plc_db import SIG_RECV_START_TRIGGER, SIG_RECV_PSN, SIG_RECV_MODEL, SIG_RECV_CHASSIS
from api.state import SYSTEM_STATES
from api.artifact import Artifact

def inspection_start_actions(data):
    print("Fetching Part data from PLC")
    ack = get_signal(SIG_RECV_START_TRIGGER)
    if ack != 1: # Handshake signal not received
        time.sleep(1)
        next_state = SYSTEM_STATES.INSPECTION_START
        data.state.update_state(next_state, force=True)
        return

    psn = get_signal(SIG_RECV_PSN)
    chassis = get_signal(SIG_RECV_CHASSIS)
    vehicle_model = get_signal(SIG_RECV_MODEL)
    print("Fetched part data:", psn, chassis, vehicle_model)

    # Initialize engine
    data.artifact = Artifact(psn, chassis, vehicle_model)

    next_state = SYSTEM_STATES.INSPECTION_RUNNING
    data.state.update_state(next_state)
