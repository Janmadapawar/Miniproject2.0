import cv2
from ultralytics import YOLO
import os
import pyttsx3
import time

# Load trained model
model = YOLO("detection/weights/best.pt")

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)   # speed
engine.setProperty('volume', 1.0) # volume

# Last alert timestamp
last_alert_time = 0
ALERT_COOLDOWN = 3  # seconds

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

# Create output folder
os.makedirs("runs/webcam_output", exist_ok=True)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Run YOLO detection
    results = model(frame, conf=0.25)
    annotated_frame = frame.copy()

    detected_without_helmet = False  # flag for this frame

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            label = model.names[cls_id]

            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()

            # Draw rectangle and label
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                annotated_frame,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # 🚨 If any "Without Helmet" found in this frame
            if label == "Without Helmet":
                detected_without_helmet = True

    # Handle alerts once per frame
    if detected_without_helmet:
        now = time.time()
        if now - last_alert_time > ALERT_COOLDOWN:
            last_alert_time = now
            print("🔊 Voice Alert: No helmet detected!")  # debug log
            engine.say("Warning! No helmet detected.")
            engine.runAndWait()

    # Show live feed
    cv2.imshow("Helmet Detection", annotated_frame)

    # Save every nth frame
    if frame_count % 10 == 0:
        out_path = f"runs/webcam_output/frame_{frame_count}.jpg"
        cv2.imwrite(out_path, annotated_frame)
        print(f"✅ Saved {out_path}")

    frame_count += 1

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("🎉 Done! Check 'runs/webcam_output/' for saved detections.")
