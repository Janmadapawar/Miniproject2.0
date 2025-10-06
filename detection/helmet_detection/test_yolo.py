from ultralytics import YOLO

# Load pre-trained YOLOv8 model
model = YOLO("yolov8n.pt")  # 'n' = nano, fastest and smallest model

# Run detection on a sample image
results = model("https://ultralytics.com/images/bus.jpg")

# Show result
for r in results:
    r.show()  # opens a window with detections
