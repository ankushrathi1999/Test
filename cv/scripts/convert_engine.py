from ultralytics import YOLO

model = YOLO(r"best_bottom_2104.onnx")

model.export(format='engine', half=True, dynamic=True, simplify=True)


# C:\Users\Administrator\Documents\MSIL-IPCluster-pipeline-new\MSIL-IPCluster-pipeline\cv\data\models\convert.py