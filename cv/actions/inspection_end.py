import logging

from api.state import SYSTEM_STATES
from utils.plc import send_signal
from config.plc_db import SIG_SEND_RESULT_MID1, SIG_SEND_RESULT_MID2

logger = logging.getLogger(__name__)

def inspection_end_actions(data):
    logger.info("Starting innspection end actions.")
    # Send data to PLC and save
    for artifact in data.artifacts:
        artifact.end_inspection()
        result1 = artifact.get_part_results_plc()

        # Cache RH result
        if data.vehicle_psn_lookup[artifact.psn] and data.vehicle_psn_lookup[artifact.psn][3] is None:
            data.vehicle_psn_lookup[artifact.psn][3] = artifact.overall_result

        if result1 is not None:
            result1 = result1[0]
            logger.info("PLC data signal: %s=%s", SIG_SEND_RESULT_MID1, result1)
            # logger.info("PLC data signal: %s=%s", SIG_SEND_RESULT_MID2, result2)
            send_signal(SIG_SEND_RESULT_MID1, result1)
            # send_signal(SIG_SEND_RESULT_MID2, result2)
        
        logger.info("Saving inspection results to database.")
        artifact.save()
    else:
        logger.info("No Artifact to save")

    # Inspection is active after at least one cycle is completed
    if not data.is_active:
        logger.info("Inspection was not active. Marking inspection as active.")
        data.is_active = True

    # Reset Cycle
    data.artifacts_prev = data.artifacts
    data.artifacts = []
    next_state = SYSTEM_STATES.INSPECTION_START_PRE
    logger.info("Inspection cycle reset. Next state: %s", next_state)
    data.state.update_state(next_state)
