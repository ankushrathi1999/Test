import logging

from processes.heartbeat_get import is_heartbeat_healthy
from api.state import SYSTEM_STATES, PLC_STATES

logger = logging.getLogger(__name__)

def inspection_start_pre_actions(data):
    hearbeat_ok = is_heartbeat_healthy()
    # hearbeat_ok = True # temp
    if hearbeat_ok:
        data.state.plc_state = PLC_STATES.HEALTHY
        logger.info("Heartbeat checks passed.")
        next_state = SYSTEM_STATES.INSPECTION_START
    else:
        data.state.plc_state = PLC_STATES.UNHEALTHY
        logger.info(f"Heartbeat checks failed.")
        # next_state = SYSTEM_STATES.INSPECTION_HALT # Do we halt inspection based on PLC Health?
        next_state = SYSTEM_STATES.INSPECTION_START
    
    logger.info("Next state: %s", next_state)
    data.state.update_state(next_state)
