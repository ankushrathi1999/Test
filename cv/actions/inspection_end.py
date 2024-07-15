import logging

from api.state import SYSTEM_STATES
from utils.plc import send_signal
from config.plc_db import SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2

logger = logging.getLogger(__name__)

def inspection_end_actions(data):
    logger.info("Starting innspection end actions.")
    # Send data to PLC and save
    if data.artifact is not None:
        data.artifact.end_inspection()
        result1, result2 = data.artifact.get_part_results_plc()
        logger.info("PLC data signal: %s=%s", SIG_SEND_RESULT_MID1, result1)
        logger.info("PLC data signal: %s=%s", SIG_SEND_RESULT_MID2, result2)
        send_signal(SIG_SEND_RESULT_MID1, result1)
        send_signal(SIG_SEND_RESULT_MID2, result2)
        logger.info("Saving inspection results to database.")
        data.artifact.save()
    else:
        logger.info("No Artifact to save")

    # Inspection is active after at least one cycle is completed
    if not data.is_active:
        logger.info("Inspection was not active. Marking inspection as active.")
        data.is_active = True

    # Reset Cycle
    data.artifact = None
    next_state = SYSTEM_STATES.INSPECTION_START_PRE
    logger.info("Inspection cycle reset. Next state: %s", next_state)
    data.state.update_state(next_state)
