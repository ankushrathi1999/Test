import time
import threading
import logging
import cv2

logger = logging.getLogger(__name__)

video_mode = False
if video_mode:
    skip_frames = 0
else:
    skip_frames = 1

def _read_frames(thread):
    while len(thread.data.video_paths) == 0:
        continue
    video_path = thread.data.video_paths[thread.video_index]
    logger.info("Start of video mamager thread: video_index=%s, video_path=%s", thread.video_index, video_path)
    cap = cv2.VideoCapture(video_path)
    count = -1
    while not thread.is_terminated:
        count += 1
        try:
            if skip_frames > 0  and count % skip_frames > 0:
                cap.grab()
                continue
            success, frame = cap.read()
            if not success:
                logger.debug("Error in video capture: %s. Resetting.", video_path)
                cap = cv2.VideoCapture(video_path)
            else:
                thread.data.frames[thread.video_index] = frame
                if video_mode:
                    time.sleep(0.1)
        except Exception as ex:
            logger.exception("Error in video manager thread.")
    thread.is_terminated = True
    logger.info("End of video_helper thread: video_index=%s, video_path=%s", thread.video_index, video_path)

class VideoManager:

    def __init__(self, data, video_index):
        self.data = data
        self.video_index = video_index
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_read_frames, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()