import cv2

def read_video_frames(video_paths):
    caps = [cv2.VideoCapture(video_path) for video_path in video_paths]
    try:
        while True:
            frames = []
            for cap in caps:
                success, frame = cap.read()
                frames.append(frame if success else None)
            yield frames
    finally:
        cap.release()