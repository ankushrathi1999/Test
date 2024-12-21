import time
import threading
import logging

logger = logging.getLogger(__name__)

def _run_state_actions(thread):
    logger.info("Start of run_state_actions thread.")
    while not thread.is_terminated:
        try:
            thread.data.state.run_actions(thread.data)
        except Exception as ex:
            logger.exception("Error in run_state_actions thread.")
        finally:
            time.sleep(0.2)
    thread.is_terminated = True
    logger.info("End of run_state_actions thread.")

class StateActions:

    def __init__(self, data):
        self.data = data
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_run_state_actions, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()