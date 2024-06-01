import time
import threading
import traceback

from utils.plc import send_signal
from config.plc_db import SIG_SEND_HEART_BIT
from config.config import config

process_config = config['process_heartbeat_send']

cycle_time = process_config.getint('cycle_time_secs')

def _heartbeat_send(thread):
    cur_bit = 0
    while not thread.is_terminated:
        try:
            # print("Heartbeat send:", cur_bit)
            send_signal(SIG_SEND_HEART_BIT, [48 + cur_bit]) # ascii for 0/1
            cur_bit = 1 - cur_bit
        except Exception as ex:
            print("Error in heartbeat send thread:", ex)
            # traceback.print_exc()
        finally:
            time.sleep(cycle_time / 2)
    thread.is_terminated = True
    print("End of heartbeat send thread")

class HeartbeatSend:

    def __init__(self):
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_heartbeat_send, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()
