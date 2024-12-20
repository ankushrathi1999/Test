import time
import logging

from utils.plc import send_signal,  get_signal
from config.plc_db import SIG_RECV_END_TRIGGER, SIG_SEND_START_TRIGGET_ACK, SIG_SEND_END_TRIGGET_ACK
from api.state import SYSTEM_STATES

logger = logging.getLogger(__name__)

def inspection_running_actions(data):
    ack = get_signal(SIG_RECV_END_TRIGGER)
    logger.debug("End trigger value: %s=%s", SIG_RECV_END_TRIGGER, ack)
    if ack is not True: # Handshake signal not received
        time.sleep(0.1)
        next_state = SYSTEM_STATES.INSPECTION_RUNNING
        logger.debug("Next state: %s", next_state)
        data.state.update_state(next_state, force=True)
        return

    logger.info("End trigger received: %s=%s", SIG_RECV_END_TRIGGER, ack)
    #logger.info("Sending end trigger acknowledgement: %s", (SIG_SEND_START_TRIGGET_ACK, [48], SIG_SEND_END_TRIGGET_ACK, [49]))
    #send_signal(SIG_SEND_START_TRIGGET_ACK, [48]) # Reset to 0
    #send_signal(SIG_SEND_END_TRIGGET_ACK, [49]) # Set to 1

    next_state = SYSTEM_STATES.INSPECTION_END
    logger.info("Next state: %s", next_state)
    data.state.update_state(next_state)
