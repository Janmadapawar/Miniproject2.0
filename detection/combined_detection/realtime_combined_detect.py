import cv2
import time
from pathlib import Path
import sys
from ultralytics import YOLO

# ----------------------------
# Add project root to path
# ----------------------------
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from detection.common.alert_system import AlertSystem

# ----------------------------
# Initialize alert system
# ----------------------------
alert = AlertSystem()

# ----------------------------
# Load YOLO models
# ----------------------------
helmet_model = YOLO("detection/helmet_detection/weights/best.pt")
emergency_model = YOLO("detection/emergency_vehicle_detection/weights/best.pt")

print("Helmet model classes:", helmet_model.names)
print("Emergency vehicle classes:", emergency_model.names)

# ----------------------------
# Initialize video capture
# ----------------------------
cap = cv2.VideoCapture(0)  # use 0 for webcam
if not cap.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

cv2.namedWindow("Combined Detection", cv2.WINDOW_NORMAL)

# ----------------------------
# Alert cooldowns
# ----------------------------
last_helmet_alert = 0
last_emergency_alert = 0
alert_cooldown = 3  # seconds

# ----------------------------
# Frame counter for throttling
# ----------------------------
frame_counter = 0
emergency_interval = 2  # run emergency detection every 2 frames

print("="*60)
print("🚦 Combined Detection Started (Helmet + Emergency Vehicles)")
print("Press 'q' to quit")
print("="*60)

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame.")
        break

    # Resize frame for faster YOLO inference
    resized_frame = cv2.resize(frame, (640, 640))
    annotated_frame = frame.copy()
    current_time = time.time()

    # ----------------------------
    # Helmet Detection (every frame)
    # ----------------------------
    results_helmet = helmet_model(resized_frame, conf=0.2)  # low conf for testing
    for r in results_helmet:
        for box in r.boxes:
            cls_id = int(box.cls)
            label = helmet_model.names[cls_id].lower()
            conf = float(box.conf)
            # Debug print
            # print("Helmet Detected:", label, conf)

            if label == "without helmet":  # exact match from your model
                # Scale coordinates to original frame size
                x1, y1, x2, y2 = [
                    int(coord * frame.shape[1]/640) if i % 2 == 0 else int(coord * frame.shape[0]/640)
                    for i, coord in enumerate(box.xyxy[0])
                ]
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(annotated_frame, f"No Helmet ({conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if current_time - last_helmet_alert > alert_cooldown:
                    alert.play_alert("no_helmet")
                    last_helmet_alert = current_time

    # ----------------------------
    # Emergency Vehicle Detection (every N frames)
    # ----------------------------
    if frame_counter % emergency_interval == 0:
        results_emergency = emergency_model(resized_frame, conf=0.2)
        for r in results_emergency:
            for box in r.boxes:
                cls_id = int(box.cls)
                label = emergency_model.names[cls_id].lower()
                conf = float(box.conf)
                # Debug print
                # print("Emergency Detected:", label, conf)

                if label == "emergency":  # exact match from your model
                    x1, y1, x2, y2 = [
                        int(coord * frame.shape[1]/640) if i % 2 == 0 else int(coord * frame.shape[0]/640)
                        for i, coord in enumerate(box.xyxy[0])
                    ]
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                    cv2.putText(annotated_frame, f"Emergency Vehicle ({conf:.2f})", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                    if current_time - last_emergency_alert > alert_cooldown:
                        alert.play_alert("emergency_vehicle")
                        last_emergency_alert = current_time

    # ----------------------------
    # Display
    # ----------------------------
    cv2.imshow("Combined Detection", annotated_frame)
    frame_counter += 1

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ----------------------------
# Cleanup
# ----------------------------
cap.release()
cv2.destroyAllWindows()

print("="*60)
print("🎉 Combined Detection Finished!")
print("="*60)
