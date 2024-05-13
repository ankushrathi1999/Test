import cv2
from threading import Lock

caps = None
caps_lock = None

def read_video_frames(video_paths):
    global caps
    global caps_lock
    caps = [cv2.VideoCapture(video_path) for video_path in video_paths]
    caps_lock = [Lock() for _ in caps]
    count = 0
    try:
        while True:
            count += 1
            frames = []
            for i, cap in enumerate(caps):
                with caps_lock[i]:
                    success, frame = cap.read()
                if not success:
                    print("Error in caps")
                    with caps_lock[0]:
                        with caps_lock[1]:
                            caps = [cv2.VideoCapture(video_path) for video_path in video_paths]
                    break
                frames.append(frame)
            else:
                yield frames
    finally:
        cap.release()