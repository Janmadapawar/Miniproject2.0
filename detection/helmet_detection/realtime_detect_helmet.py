import sys
from pathlib import Path

# Fix module import issue
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import cv2
from ultralytics import YOLO
import os
import time
from detection.common.alert_system import AlertSystem

# ===============================
# Helmet Detection (Integrated with Common Alert System)
# ===============================

# Load YOLO model
model = YOLO("detection/helmet_detection/weights/best.pt")
alert = AlertSystem()

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

# Output folder
os.makedirs("runs/helmet_webcam_output", exist_ok=True)

frame_count = 0
last_alert_time = 0
alert_cooldown = 3  # seconds between alerts to prevent spamming

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # 🔹 Enhance visibility and contrast (helps side angles)
    frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=15)

    # YOLO detection
    results = model(frame, conf=0.25, iou=0.5)
    annotated_frame = frame.copy()
    detected_without_helmet = False

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            label = model.names[cls_id].lower()

            x1, y1, x2, y2 = box.xyxy[0].int().tolist()

            # Set color depending on detection
            color = (0, 0, 255) if "without helmet" in label or "no helmet" in label else (0, 255, 0)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated_frame,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            # Check for violation
            if "without helmet" in label or "no helmet" in label:
                detected_without_helmet = True

    # ⚠️ Trigger central alert (with cooldown)
    current_time = time.time()
    if detected_without_helmet and (current_time - last_alert_time > alert_cooldown):
        print("⚠️ No helmet detected! Triggering alert...")
        alert.play_alert("no_helmet")
        last_alert_time = current_time

    # Show live feed
    cv2.imshow("Helmet Detection", annotated_frame)

    # Save every 10th frame (optional)
    if frame_count % 10 == 0:
        out_path = f"runs/helmet_webcam_output/frame_{frame_count}.jpg"
        cv2.imwrite(out_path, annotated_frame)

    frame_count += 1

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("🎉 Helmet detection finished! Output saved in 'runs/helmet_webcam_output/'")
