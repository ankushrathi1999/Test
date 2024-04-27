import ffmpegcv
import cv2
from threading import Lock
# import subprocess
import numpy as np

# res = [2560, 1920]
# def _read_video_frames_ffmpeg(video_path):
#     command = [
#         # r"C:\Users\Administrator\Downloads\ffmpeg-2024-04-21-git-20206e14d7-full_build\ffmpeg-2024-04-21-git-20206e14d7-full_build\bin\ffplay",
#         r"C:\Users\Administrator\Downloads\nvffmpeg\binaries\ffplay"
#         "-i",
#         video_path,
#         "-fflags",
#         "nobuffer",
#         "-max_probe_packets",
#         "1",
#         "-flags",
#         "+low_delay",
#         "-probesize",
#         "32",
#         "-tune",
#         "zero_latency",
#         "-f",
#         "image2pipe",
#         "-pix_fmt",
#         "rgb24",
#         "-vcodec",
#         "rawvideo",
#         "-"
#     ]

#     pipe = subprocess.Popen(
#         command,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.DEVNULL,
#         bufsize=res[0]*res[1]*3,
#     )

#     while pipe.poll() is None:
#         frame = pipe.stdout.read(res[0] * res[1] * 3)
#         if len(frame) > 0:
#             array = np.frombuffer(frame, dtype="uint8")
#             array = array.reshape((res[1], res[0], 3))
#             img = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
#             yield img

# def read_video_frames(video_paths):
#     frame_itrs = [_read_video_frames_ffmpeg(video_path) for video_path in video_paths]
#     while True:
#         try:
#             frames = [next(itr) for itr in frame_itrs]
#         except StopIteration:
#             print("Video reader terminated")
#             frame_itrs = [_read_video_frames_ffmpeg(video_path) for video_path in video_paths]
#             continue
#         yield frames

# skip_frame = 1

# def read_video_frames(video_paths):
#     global caps
#     global caps_lock
#     caps = [ffmpegcv.VideoCaptureStreamRT(video_path) for video_path in video_paths]
#     caps_lock = [Lock() for _ in caps]
#     count = 0
#     try:
#         while True:
#             count += 1
#             frames = []
#             for i, cap in enumerate(caps):
#                 with caps_lock[i]:
#                     success, frame = cap.read()
#                 if not success:
#                     print("Error in caps")
#                     with caps_lock[0]:
#                         with caps_lock[1]:
#                             caps = [ffmpegcv.VideoCaptureStreamRT(video_path) for video_path in video_paths]
#                     break
#                 frames.append(np.copy(frame))
#             else:
#                 yield frames
#     finally:
#         cap.release()

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
                # if count % skip_frame == 0:
                yield frames
    finally:
        cap.release()