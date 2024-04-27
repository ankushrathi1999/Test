# from ultralytics import YOLO
import cv2

# from config.models import ModelConfig
from utils.live_display import prepare_live_display
from utils.image_utils import plot_one_box

from api.data import Data
from api.artifact import Artifact

data = Data()
data.artifact = Artifact("PSN", "XYZ", "XYZ")

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
            'class_id': cl,
            'color': model_config.class_colors[cl_name],
            'confidence': cn,
            'bbox': bx,
            'result_type': result_type,
        })
    return processed

window_name_top = 'debug1'
window_name_bottom = 'debug2'

cv2.namedWindow(window_name_top, cv2.WINDOW_NORMAL)
# cv2.namedWindow(window_name_bottom, cv2.WINDOW_NORMAL)

video_path_top = "rtsp://admin:Eternal$12@192.168.1.64:554/h264/ch1/main/av_stream"#"rtsp://admin:Eternal$12@192.168.1.64:554/Streaming/channels/101"
video_path_bottom = "rtsp://admin:Eternal$12@192.168.1.65:554/h264/ch1/main/av_stream"#"rtsp://admin:Eternal$12@192.168.1.65:554/Streaming/channels/101"
cap_top = cv2.VideoCapture(video_path_top)
cap_bottom = cv2.VideoCapture(video_path_bottom)

top_cam_model_path = r"C:\Users\Administrator\Downloads\models\best_top_2104_iter2.pt"
bottom_cam_model_path = r"C:\Users\Administrator\Downloads\models\best_bottom_2104.pt"
# model_top_cam = YOLO(top_cam_model_path)
# model_bottom_cam = YOLO(bottom_cam_model_path)

skip_frames = 15
frame_count = 0

while True:
    frame_count += 1
    success1, frame_top = cap_top.read()
    success2, frame_bottom = cap_bottom.read()
    if not success1 or not success2:
        print("Stream closed", success1, success2)
        cap_top = cv2.VideoCapture(video_path_top)
        cap_bottom = cv2.VideoCapture(video_path_bottom)
        continue
    
    # if frame_count % skip_frames > 0:
    #     continue

    # results_top = model_top_cam.predict(frame_top, conf=0.05, verbose=False, imgsz=ModelConfig.top_cam.imgsz)
    # results_top = _process_result(results_top[0], ModelConfig.top_cam, 'top')
    
    # results_bottom = model_bottom_cam.predict(frame_bottom, conf=0.05, verbose=False, imgsz=ModelConfig.bottom_cam.imgsz)
    # results_bottom = _process_result(results_bottom[0], ModelConfig.bottom_cam, 'bottom')

    # all_results = [*results_top, *results_bottom]
    all_results = []
    for result in all_results:
        class_bbox = result['bbox']
        class_name = result['name']
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
            f'{class_name}_{detect_confidence}',
            3
        )
    
    data.artifact.update(all_results, frame_top, frame_bottom)
    display_image =  prepare_live_display(frame_top, frame_bottom, data)
    
    cv2.imshow(window_name_top, display_image)
    # cv2.imshow(window_name_bottom, frame_bottom)

    # Key handling
    k = cv2.waitKey(1)
    if k == 27:  # Escape/Quit
        print("Quit confirmed.")
        break
