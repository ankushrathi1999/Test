import time
import threading
import logging

from utils.plc import flush_plc_data

logger = logging.getLogger(__name__)

def _flush_plc_data(thread):
    logger.info("Start of PLCIO thread.")
    while not thread.is_terminated:
        try:
            flush_plc_data()
        except Exception as ex:
            logger.exception("Error in PLCIO thread.")
        finally:
            time.sleep(0.1)
    thread.is_terminated = True
    logger.info("End of PLCIO thread.")

class PLCIO:

    def __init__(self):
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_flush_plc_data, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()