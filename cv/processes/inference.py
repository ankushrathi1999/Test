from ultralytics import YOLO
import cv2
import os
import threading
import logging
from collections import defaultdict

from config.models import classification_models, detection_models
from utils.image_utils import plot_one_box, draw_confirmation_prompt
from utils.live_display import prepare_live_display
from config.config import config
from config.colors import color_red, color_green
from api.detection import DetectionDetails, ClassificationDetails, FinalDetails, DetectionResult

logger = logging.getLogger(__name__)

process_config = config['process_inference']
models_base_path = process_config.get('models_base_path')
window_name = process_config.get('window_name')

CONFIRM_MODE_QUIT = "quit"
CONFIRM_MODE_RESET = "reset"
CONFIRM_MODE_SUBMIT = "submit"

def _inference_loop(thread):
    logger.info("Start of inference thread.")
    data = thread.data
    try:
        models_detect = [YOLO(os.path.join(models_base_path, f'{m.name}.pt'), task="detect") for m in detection_models]
        for model, model_config in zip(models_detect, detection_models):
            logger.info("Detection model: %s", model_config.name)
            logger.info("Model loaded labels: %s", model.names)
        models_cls = [YOLO(os.path.join(models_base_path, f'{m.name}.pt')) for m in classification_models]
        for model, model_config in zip(models_cls, classification_models):
            logger.info("Classification model: %s", model_config.name)
            logger.info("Model loaded labels: %s", model.names)
        
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        confirm_mode = None
        while True:
            if thread.is_terminated:
                break

            if len(data.frames) != len(data.video_config):
                continue

            frames_orig = {cam_type: frame_cam.copy() for cam_type, frame_cam in data.frames.items()}

            # Detections
            detections = []
            for video_config in data.video_config:
                cam_type = video_config['code']
                frame_cam = frames_orig[cam_type]
                cur_artifact = video_config['artifact']
                if frame_cam is None:
                    continue
                if len(data.artifacts) == 0: # skip detections when vehicle is not available
                    continue
                for model, model_config in zip(models_detect, detection_models):
                    if cam_type not in model_config.target_cams: 
                        continue
                    if model_config.tracking:
                        results = model.track(frame_cam, conf=0.25, verbose=False, persist=True)
                    else:
                        results = model.predict(frame_cam, conf=0.25, verbose=False)
                    result = results[0]
                    try:
                        bboxs = result.boxes.xyxy.cpu()
                        conf = result.boxes.conf.cpu()
                        cls = result.boxes.cls.cpu().tolist()
                        track_ids = result.boxes.id.cpu().tolist() if model_config.tracking else [None for _ in cls]
                    except Exception as ex:
                        #print("No detections")
                        bboxs = []
                        conf = []
                        cls = []
                        track_ids = []
                    print("D:", model_config.name, cam_type, len(bboxs))
                    processed = []
                    for bbox, confidence, class_idx, tracking_id in zip(bboxs, conf, cls, track_ids):
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

                        # Class ROI check
                        detection_roi = model_config.class_cam_rois.get(class_id, {}).get(cam_type)
                        if detection_roi is not None:
                            img_w = frame_cam.shape[1]
                            print("Debug:", cam_type, class_id, img_w, detection_roi, bbox)
                            detection_x1, detection_x2 = [x * img_w for x in detection_roi]
                            # if bbox[0] < detection_x1 or bbox[1] > detection_x2:
                            if bbox[2] < detection_x1 or bbox[0] > detection_x2:
                                continue

                        # try:
                        #     class_id_new = PartDetectionModel.get_processed_class(class_id, data.artifact.vehicle_category, data.artifact.vehicle_type)
                        #     if class_id_new != class_id:
                        #         logger.debug("Class ID updated. class_id=%s class_id_new=%s vehicle_category=%s vehicle_type=%s", class_id, class_id_new, data.artifact.vehicle_category, data.artifact.vehicle_type)
                        #         class_id = class_id_new
                        # except:
                        #     pass
                        detection = DetectionDetails(
                            class_id, class_name,  model_config.name, confidence, class_color, bbox, cam_type, cur_artifact, tracking_id=tracking_id)
                        detection.final_details = FinalDetails(class_name, color_green, DetectionResult.NOT_EVALUATED)
                        processed.append(detection)
                    detections.extend(processed)

            print("Num detections:", len(detections))

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
                    artifact = [a for a in data.artifacts if a.artifact_config['code'] == detection.artifact][0] if len(data.artifacts) else None
                    frame_cam = frames_orig[detection.cam_type]
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
                    try:
                        part_number = model_config.get_part_number(detection.class_id, class_id, artifact.vehicle_category, artifact.vehicle_type)
                    except:
                        part_number = class_id

                        
                    detection.classification_details = ClassificationDetails(
                        class_id, class_name, part_number, is_flip, model_config.name, confidence, class_color)
                    detection.final_details = FinalDetails(class_name, color_red, DetectionResult.NOT_EVALUATED)
            
            # Update data
            for artifact in (data.artifacts or []):
                frames_artifact = {video['code']: data.frames[video['code']] for video in data.video_config if video['artifact'] == artifact.artifact_config['code']}
                detection_groups_artifact = {class_id: [d for d in detections if d.artifact == artifact.artifact_config['code']] for class_id, detections in detection_groups.items()}
                artifact.update(detection_groups_artifact, frames_artifact)

            # Plot
            for detection in detections:
                artifact = [a for a in data.artifacts if a.artifact_config['code'] == detection.artifact][0] if len(data.artifacts) else None
                # print("Artifact:", artifact is None, artifact.inspection_flag, detection.final_details.ignore)
                if artifact is None or artifact.inspection_flag != 1 or detection.final_details.ignore:
                    continue
                class_bbox = detection.bbox
                label = detection.final_details.label
                color = detection.final_details.color
                confidence_detect = round(detection.confidence, 2)
                confidence_cls = round(detection.classification_details.confidence, 2) if detection.classification_details is not None else 0
                label_position = detection.final_details.label_position
                label_offset = detection.final_details.label_offset

                frame_cam = frames_orig[detection.cam_type]

                plot_one_box(
                    class_bbox,
                    frame_cam,
                    color=color,
                    label=f'{label}_{confidence_detect}_{confidence_cls}',
                    line_thickness=3,
                    label_position=label_position,
                    label_offset=label_offset
                )

            # Generate display layout and stats
            display_image =  prepare_live_display(frames_orig, data)
            
            # Render confirm popup
            if confirm_mode:
                confirm_text = {
                    CONFIRM_MODE_QUIT: "Are you sure you want to quit?",
                    CONFIRM_MODE_RESET: "Are you sure you want to reset the application?",
                    CONFIRM_MODE_SUBMIT: "Submit for Inspection?",
                }.get(confirm_mode)
                if not confirm_text:
                    logger.warn("Unhandled confirm mode: %s", confirm_mode)
                else:
                    draw_confirmation_prompt(display_image, confirm_text, accept_button="Enter", reject_button="Escape")

            cv2.imshow(window_name, display_image)

            # Key handling
            k = cv2.waitKey(1)
            if k == 27:  # Escape/Quit
                if confirm_mode:
                    logger.info("Popup rejected: %s", confirm_mode)
                    confirm_mode = None
                else:
                    logger.info("Quit selected.")
                    confirm_mode = CONFIRM_MODE_QUIT
            elif k == 13: # Enter
                logger.info("Handling confirm: %s", confirm_mode)
                if confirm_mode == CONFIRM_MODE_QUIT:
                    logger.info("Quit confirmed.")
                    break

            
    except Exception as ex:
        logger.exception("Inference loop thread error.")
    finally:
        thread.is_terminated = True
        logger.info("End of inference loop thread.")


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
