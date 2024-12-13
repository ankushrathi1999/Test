import time
import logging

from utils.plc import send_signal,  get_signal, get_data_block
from config.plc_db import (
    SIG_RECV_START_TRIGGER, SIG_RECV_PSN, SIG_RECV_MODEL, SIG_RECV_CHASSIS, SIG_RECV_COLOR, SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2,
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
    color_code = get_signal(SIG_RECV_COLOR)
    result = None
    psn_chassis_block = get_data_block(0,11)
    data.vehicle_psn_lookup[psn] = [chassis, vehicle_model, color_code, result, psn_chassis_block]
    logger.info("Fetched part data: psn=%s, chassis=%s, vehicle_model=%s, color_code=%s", psn, chassis, vehicle_model, color_code)

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
        try:
            data.artifacts = []
            for artifact in artifacts_config['artifacts']:
                psn_cur = psn + artifact.get('psn_offset', 0)
                psn_data = data.vehicle_psn_lookup.get(psn_cur, ("-", "-", "-"))
                data.artifacts.append(Artifact(artifact, psn_cur, psn_data[0], psn_data[1], psn_data[2], data))
        except Exception as ex:
            logger.error("Artifacts not intialized due to error: %s", ex)
            data.artifacts = []
    else:
        logger.info("Inspection active flag is off. Skipping current inspection.")

    next_state = SYSTEM_STATES.INSPECTION_RUNNING
    logger.info("Next state: %s", next_state)
    data.state.update_state(next_state)
