from ultralytics import YOLO
import cv2
import os
import threading
import traceback
from collections import defaultdict

from config.models import classification_models, detection_models, BezelSwitchClassificationModel, PartDetectionModel
from utils.image_utils import plot_one_box, draw_confirmation_prompt
from utils.live_display import prepare_live_display
from config.config import config
from config.colors import color_red, color_green
from api.detection import DetectionDetails, ClassificationDetails, FinalDetails, DetectionResult

process_config = config['process_inference']
models_base_path = process_config.get('models_base_path')
window_name = process_config.get('window_name')
video_path_top = process_config.get('video_path_top')
video_path_bottom = process_config.get('video_path_bottom')
video_path_up = process_config.get('video_path_up')

CONFIRM_MODE_QUIT = "quit"
CONFIRM_MODE_RESET = "reset"
CONFIRM_MODE_SUBMIT = "submit"

def _inference_loop(thread):
    data = thread.data
    data.video_paths = [video_path_top, video_path_bottom, video_path_up]
    try:
        models_detect = [YOLO(os.path.join(models_base_path, f'{m.name}.pt'), task="detect") for m in detection_models]
        models_cls = [YOLO(os.path.join(models_base_path, f'{m.name}.pt')) for m in classification_models]
        
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

            # Detections
            detections = []
            for frame_cam, cam_type in [
                (frame_top, 'top'),
                (frame_bottom, 'bottom'),
                (frame_up, 'up'),
            ]:
                if frame_cam is None:
                    continue
                if data.artifact is None: # skip detections when vehicle is not available
                    continue
                for model, model_config in zip(models_detect, detection_models):
                    if cam_type not in model_config.target_cams:
                        continue
                    results = model.predict(frame_cam, conf=0.25, verbose=False)
                    result = results[0]
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
                    for bbox, confidence, class_idx in zip(bboxs, conf, cls):
                        class_idx = int(class_idx)
                        class_id = model_config.ordered_class_list[class_idx]
                        if class_id is None: # skipped class
                            continue
                        if cam_type not in model_config.class_cams.get(class_id, set()):
                            continue
                        confidence = float(confidence)
                        if confidence < model_config.class_confidence[class_id]: # confidence filter
                            continue
                        class_name = model_config.class_names[class_id]
                        bbox = [int(x) for x in bbox]
                        class_color = model_config.class_colors[class_id]
                        try:
                            print("Get processed class before:", class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                            class_id = PartDetectionModel.get_processed_class(class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                            print("Get processed class after:", class_id)
                        except:
                            pass
                        detection = DetectionDetails(
                            class_id, class_name,  model_config.name, confidence, class_color, bbox, cam_type)
                        detection.final_details = FinalDetails(class_name, color_green, DetectionResult.NOT_EVALUATED)
                        processed.append(detection)
                    detections.extend(processed)

            # Group detections by class
            detection_groups = defaultdict(list)
            for detection in detections:
                detection_groups[detection.class_id].append(detection)

            # Classifications
            for model, model_config in zip(models_cls, classification_models):
                targets = []
                for class_id in model_config.target_detections:
                    targets.extend(detection_groups.get(class_id, []))
                if len(targets) == 0:
                    continue
                for detection in targets:
                    frame_cam = {
                        'top': frame_top_orig,  
                        'bottom': frame_bottom_orig,  
                        'up': frame_up_orig,  
                    }[detection.cam_type]
                    class_bbox = detection.bbox
                    img_crop = frame_cam[class_bbox[1]:class_bbox[3],class_bbox[0]:class_bbox[2]]
                    results = model.predict(img_crop, conf=0.25, verbose=False)
                    result = results[0]
                    pred_class_idx = result.probs.top1
                    class_id = model_config.ordered_class_list[pred_class_idx] # todo: class_id None and confidence filters
                    class_name = model_config.class_names[class_id]
                    confidence = round(float(result.probs.data.max()), 2)
                    class_color = model_config.class_colors[class_id]

                    # Part number
                    is_flip = False
                    if data.artifact and model_config is BezelSwitchClassificationModel:
                        part_number, is_flip = BezelSwitchClassificationModel.get_part_number(None, class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                        print("Bezel switch get part nuimber:", part_number, is_flip, class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                    else:
                        try:
                            part_number = model_config.get_part_number(detection.class_id, class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                            print("Classification get part nuimber:", part_number, detection.class_id, class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                        except:
                            print("Get part number failed. Using class id:", class_id)
                            part_number = class_id

                    detection.classification_details = ClassificationDetails(
                        class_id, class_name, part_number, is_flip, model_config.name, confidence, class_color)
                    detection.final_details = FinalDetails(class_name, color_red, DetectionResult.NOT_EVALUATED)
            
            # Update data
            if data.artifact:
                data.artifact.update(detection_groups, frame_top_orig, frame_bottom_orig, frame_up_orig)

            # Plot
            for detection in detections:
                if data.artifact is None or not data.artifact.inspection_flag == 1 or detection.final_details.ignore:
                    continue
                class_bbox = detection.bbox
                label = detection.final_details.label
                color = detection.final_details.color
                confidence_detect = round(detection.confidence, 2)
                confidence_cls = round(detection.classification_details.confidence, 2) if detection.classification_details is not None else 0
                label_position = detection.final_details.label_position
                label_offset = detection.final_details.label_offset

                frame_cam = {
                    'top': frame_top,  
                    'bottom': frame_bottom,  
                    'up': frame_up,  
                }[detection.cam_type]

                plot_one_box(
                    class_bbox,
                    frame_cam,
                    color=color,
                    label=f'{label}',#_{confidence_detect}_{confidence_cls}',
                    line_thickness=3,
                    label_position=label_position,
                    label_offset=label_offset
                )

            # Generate display layout and stats
            display_image =  prepare_live_display(frame_top, frame_bottom, frame_up, data)
            
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
