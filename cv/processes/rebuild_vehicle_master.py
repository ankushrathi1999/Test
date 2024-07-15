import time
import threading
import logging

from config.config import config, load_vehicle_parts_lookup
from utils.build_vehicle_master import build_vehicle_master

logger = logging.getLogger(__name__)

process_config = config['process_heartbeat_send']
cycle_time = process_config.getint('cycle_time_secs')

def _rebuild_vehicle_master(thread):
    logger.info("Start of rebuild_vehicle_master thread.")
    while not thread.is_terminated:
        time.sleep(60)
        try:
            build_vehicle_master()
            load_vehicle_parts_lookup()
            logger.debug("Reloaded vehicle parts lookup")
        except Exception:
            logger.exception("Faile to regenerate vehicle master")
    thread.is_terminated = True
    logger.info("End of rebuild_vehicle_master thread.")

class RebuildVehicleMaster:

    def __init__(self):
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_rebuild_vehicle_master, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()
