import time
import threading
import logging

from utils.plc import get_signal
from config.plc_db import SIG_RECV_HEART_BIT
from config.config import config

logger = logging.getLogger(__name__)

process_config = config['process_heartbeat_get']

cycle_time = process_config.getint('cycle_time_secs')
cycle_poll_frequency = process_config.getint('cycle_poll_frequency')
health_check_duration = process_config.getint('hearbeat_history_secs')  # Duration in seconds to check for heartbeat health

heartbeat_history = []

def is_heartbeat_healthy():
    return not all(heartbeat_history[i] == heartbeat_history[i + 1] for i in range(len(heartbeat_history) - 1))

def _heartbeat_get(thread):
    logger.info("Start of heartbeat get thread.")
    while not thread.is_terminated:
        try:
            cur_bit = get_signal(SIG_RECV_HEART_BIT)
            logger.debug('Heart bit received: %s', cur_bit)

            # Add the current bit to the history and ensure it doesn't exceed the health_check_duration
            heartbeat_history.append(cur_bit)
            if len(heartbeat_history) > health_check_duration * cycle_poll_frequency:
                heartbeat_history.pop(0)
        except Exception as ex:
            logger.exception("Error in heartbeat get thread.")
        finally:
            time.sleep(cycle_time / cycle_poll_frequency)
    thread.is_terminated = True
    logger.info("End of heartbeat get thread")

class HeartbeatGet:

    def __init__(self):
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_heartbeat_get, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()
