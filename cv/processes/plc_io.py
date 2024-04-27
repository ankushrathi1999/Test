import time
import threading
import traceback

from utils.plc import flush_plc_data

def _flush_plc_data(thread):
    while not thread.is_terminated:
        try:
            flush_plc_data()
        except Exception as ex:
            print("Error in PLCIO thread:", ex)
            traceback.print_exc()
        finally:
            time.sleep(0.1)
    thread.is_terminated = True
    print("End of PLCIO thread")

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