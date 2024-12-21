from ultralytics import YOLO

model = YOLO(r"scripts\models\best_bottom_2104.pt")

model.export(format='engine', half=True, dynamic=True, simplify=True)


# C:\Users\Administrator\Documents\MSIL-IPCluster-pipeline-new\MSIL-IPCluster-pipeline\cv\data\models\convert.py