import time
import logging

from utils.plc import send_signal,  get_signal
from config.plc_db import (
    SIG_RECV_START_TRIGGER, SIG_RECV_PSN, SIG_RECV_MODEL, SIG_RECV_CHASSIS, SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2,
    SIG_SEND_START_TRIGGET_ACK, SIG_SEND_END_TRIGGET_ACK
)
from api.state import SYSTEM_STATES
from api.artifact import Artifact
from utils.artifact_utils import artifacts_config

logger = logging.getLogger(__name__)

def inspection_start_actions(data):
    logger.debug("Fetching Part data from PLC.")
    ack = get_signal(SIG_RECV_START_TRIGGER)
    if ack is not True: # Handshake signal not received
        next_state = SYSTEM_STATES.INSPECTION_START
        logger.debug("Ack not received. Next State=%s Sleep=1sec", next_state)        
        time.sleep(0.1)
        data.state.update_state(next_state, force=True)
        return

    psn = get_signal(SIG_RECV_PSN)
    chassis = get_signal(SIG_RECV_CHASSIS)
    vehicle_model = get_signal(SIG_RECV_MODEL)
    logger.info("Fetched part data: psn=%s, chassis=%s, vehicle_model=%s", psn, chassis, vehicle_model)

    # Reset results on PLC
    logger.info("Sending start trigger acknowledgement: %s", (SIG_SEND_END_TRIGGET_ACK, [48], SIG_SEND_START_TRIGGET_ACK, [49]))
    send_signal(SIG_SEND_END_TRIGGET_ACK, [48]) # Reset to 0
    send_signal(SIG_SEND_START_TRIGGET_ACK, [49]) # Set to 1
    reset_value = [0 for _ in range(23)]
    logger.info("Resetting PLC results: %s", (SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2, reset_value))
    send_signal(SIG_SEND_RESULT_MID1, reset_value)
    send_signal(SIG_SEND_RESULT_MID2, reset_value)

    # Initialize engine
    if data.is_active:
        logger.info("Inspection is active. Initializing artifact.")
        data.artifacts = [
            Artifact(artifact, psn + artifact.get('psn_offset', 0), chassis, vehicle_model, data)
            for artifact in artifacts_config['artifacts']
        ]
    else:
        logger.info("Inspection active flag is off. Skipping current inspection.")

    next_state = SYSTEM_STATES.INSPECTION_RUNNING
    logger.info("Next state: %s", next_state)
    data.state.update_state(next_state)
