from ultralytics import YOLO
import cv2
import random
import os
import pyshine as ps


def plot_one_box(x, img, color=None, label=None, line_thickness=3):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


def plot_one_box_b(x, img, color=None, label=None, line_thickness=3):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        c2, c1 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


# Load a model
model = YOLO("best3.pt")

class_names = model.names
print('Class Names: ', class_names)
colors = [[random.randint(0, 255) for _ in range(3)] for _ in class_names]
save = True

cap = cv2.VideoCapture('Data/01_20240328105915367_1.mp4')
# cap = cv2.VideoCapture('rtsp://admin:eternal@12@192.168.1.13:554/cam/realmonitor?channel=1')
original_video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
original_video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
if save:
    out_vid = cv2.VideoWriter(f"POC/output{len(os.listdir('POC'))}.mp4", 
                         cv2.VideoWriter_fourcc(*'mp4v'),
                         fps, (original_video_width, original_video_height))

master_list = [1, 2, 9, 11, 12, 16, 17, 21]

# Setup Window
# cv2.namedWindow('img', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('img', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success:
        print('[INFO] Failed...')
        break
    
    class_id_list = []
    results = model.predict(img, conf=0.25)
    for result in results:
        bboxs = result.boxes.xyxy.cpu()
        conf = result.boxes.conf.cpu()
        cls = result.boxes.cls.cpu()
        for bbox, cnf, cs in zip(bboxs, conf, cls):
            if int(cs) != 10:
                xmin = int(bbox[0])
                ymin = int(bbox[1])
                xmax = int(bbox[2])
                ymax = int(bbox[3])
                class_id_list.append(int(cs))
                if int(cs) in [16, 17, 18, 19]:
                    plot_one_box_b(
                        [xmin, ymin, xmax, ymax], img,
                        colors[int(cs)], f'{class_names[int(cs)]}', # {float(cnf):.3}',
                        3
                    )
                else:
                    plot_one_box(
                        [xmin, ymin, xmax, ymax], img,
                        colors[int(cs)], f'{class_names[int(cs)]}', # {float(cnf):.3}',
                        3
                    )
    
    if len(class_id_list) == 0:
        ps.putBText(img,'Waiting For Part',text_offset_x=20,text_offset_y=40,vspace=20,hspace=10, font_scale=2.0,background_RGB=(255,255,0),text_RGB=(255,255,255))
    elif (len(list(set(master_list) - set(class_id_list))) == 0):
        ps.putBText(img,'OK',text_offset_x=20,text_offset_y=40,vspace=20,hspace=10, font_scale=2.0,background_RGB=(0,255,0),text_RGB=(255,255,255))
    else:
        ps.putBText(img,'NOT OK',text_offset_x=20,text_offset_y=40,vspace=20,hspace=10, font_scale=2.0,background_RGB=(255,0,0),text_RGB=(255,255,255))
    
    # print(class_id_list)
    # neg_list = list(set(master_list) - set(class_id_list))
    # print(neg_list)
    # cv2.putText(
    #     img, f'{[class_names[x] for x in neg_list]}', (20, 160),
    #     cv2.FONT_HERSHEY_PLAIN, 2,
    #     (0, 0, 255), 2
    # )
    # Write Video
    if save:
        out_vid.write(img)

    img  = cv2.resize(img, (640, 480))
    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
if save:
    out_vid.release()
cv2.destroyAllWindows()
