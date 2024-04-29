from ultralytics import YOLO
import cv2
import threading
import traceback

from config.models import ModelConfig
from utils.image_utils import plot_one_box, draw_confirmation_prompt
from utils.video_reader import read_video_frames
from utils.live_display import prepare_live_display
from config.config import config

process_config = config['process_inference']
top_cam_model_path = process_config.get('top_cam_model_path')
bottom_cam_model_path = process_config.get('bottom_cam_model_path')
window_name = process_config.get('window_name')
video_path_top = process_config.get('video_path_top')
video_path_bottom = process_config.get('video_path_bottom')
video_path_up = process_config.get('video_path_up')

CONFIRM_MODE_QUIT = "quit"
CONFIRM_MODE_RESET = "reset"
CONFIRM_MODE_SUBMIT = "submit"

def _process_result(result, model_config, result_type):
    try:
        bboxs = result.boxes.xyxy.cpu()
        conf = result.boxes.conf.cpu()
        cls = result.boxes.cls.cpu().tolist()
    except Exception as ex:
        #print("No detections")
        bboxs = []
        conf = []
        cls = []
    processed = []
    for bx, cn, cl in zip(bboxs, conf, cls):
        cl = int(cl)
        cl_name = model_config.class_names[cl] if cl < len(model_config.class_names) else None
        if cl_name is None:
            continue
        bx = [int(x) for x in bx]
        cn = float(cn)
        if cn < model_config.class_confidence[cl_name]:
            continue
        processed.append({
            'name': cl_name,
            'desc': model_config.class_desc[cl_name],
            'class_id': cl,
            'color': model_config.class_colors[cl_name],
            'confidence': cn,
            'bbox': bx,
            'result_type': result_type,
        })
    return processed

def _inference_loop(thread):
    data = thread.data
    data.video_paths = [video_path_top, video_path_bottom, video_path_up]
    try:
        # Load models
        model_top_cam = YOLO(top_cam_model_path, task="detect")
        model_bottom_cam = YOLO(bottom_cam_model_path, task="detect")

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        confirm_mode = None
        while True:
            if thread.is_terminated:
                break

            frame_top = data.frames.get(0)
            frame_bottom = data.frames.get(1)
            frame_up = data.frames.get(2)
            if frame_top is None or frame_bottom is None or frame_up is None:
                continue

            frame_top_orig = frame_top.copy()
            frame_bottom_orig = frame_bottom.copy()
            frame_up_orig = frame_up.copy()

            # Top cam detections
            if frame_top is not None:
                results_top = model_top_cam.predict(frame_top, conf=0.05, verbose=False)
                results_top = _process_result(results_top[0], ModelConfig.top_cam, 'top')
            else:
                results_top = []

            # Bottom cam detections
            if frame_bottom is not None:
                results_bottom = model_bottom_cam.predict(frame_bottom, conf=0.05, verbose=False)
                results_bottom = _process_result(results_bottom[0], ModelConfig.bottom_cam, 'bottom')
            else:
                results_bottom = []

            all_results = [*results_top, *results_bottom]
            for result in all_results:
                class_bbox = result['bbox']
                class_name = result['name']
                class_desc = result['desc']
                class_color = result['color']
                detect_confidence = round(result['confidence'], 2)
                result_type = result['result_type']

                target_frame = None
                if result_type == "top":
                    target_frame = frame_top
                elif result_type == "bottom":
                    target_frame = frame_bottom

                plot_one_box(
                    class_bbox,
                    target_frame,
                    class_color,
                    f'{class_desc}_{detect_confidence}',
                    3
                )

            if data.artifact is not None:
                data.artifact.update(all_results, frame_top_orig, frame_bottom_orig, frame_up_orig)

            # Generate display layout and stats
            display_image =  prepare_live_display(frame_top, frame_bottom, data)
            
            # Render confirm popup
            if confirm_mode:
                confirm_text = {
                    CONFIRM_MODE_QUIT: "Are you sure you want to quit?",
                    CONFIRM_MODE_RESET: "Are you sure you want to reset the application?",
                    CONFIRM_MODE_SUBMIT: "Submit for Inspection?",
                }.get(confirm_mode)
                if not confirm_text:
                    print("Unhandled confirm mode:", confirm_mode)
                else:
                    draw_confirmation_prompt(display_image, confirm_text, accept_button="Enter", reject_button="Escape")

            cv2.imshow(window_name, display_image)

            # Key handling
            k = cv2.waitKey(1)
            if k == 27:  # Escape/Quit
                if confirm_mode:
                    print("Popup rejected:", confirm_mode)
                    confirm_mode = None
                else:
                    print("Quit selected.")
                    confirm_mode = CONFIRM_MODE_QUIT
            elif k == 13: # Enter
                print("Handling confirm:", confirm_mode)
                if confirm_mode == CONFIRM_MODE_QUIT:
                    print("Quit confirmed.")
                    break

            
    except Exception as ex:
        print("Inference loop thread error:", ex)
        traceback.print_exc()
    finally:
        thread.is_terminated = True
        print("End of inference loop thread.")


class InferenceLoop:

    def __init__(self, data):
        self.data = data
        self.runner = None
        self.is_terminated = False

    def start(self):
        self.runner = threading.Thread(target=_inference_loop, args=(self,))
        self.runner.start()

    def stop(self):
        self.is_terminated = True

    def wait(self):
        self.runner.join()
