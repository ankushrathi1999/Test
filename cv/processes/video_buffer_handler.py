import time
import threading
import traceback

import utils.video_reader as vr

def _clear_video_buffer(thread):
    while not thread.is_terminated:
        try:
            if vr.caps is not None:
                for i, cap in enumerate(vr.caps):
                    with vr.caps_lock[i]:
                        try:
                            print("Grab")
                            cap.grab()
                        except:
                            pass
                time.sleep(0.01)
        except Exception as ex:
            print("Error in video_helper thread:", ex)
            traceback.print_exc()
    thread.is_terminated = True
    print("End of video_helper thread")

class VideoBufferHandler:

    def __init__(self):
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_clear_video_buffer, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()