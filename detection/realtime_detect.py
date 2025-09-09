import cv2
from ultralytics import YOLO
import os

# Load trained model
model = YOLO("detection/weights/best.pt")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam")
    exit()

# Create output folder
output_dir = "runs/webcam_output"
os.makedirs(output_dir, exist_ok=True)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Run YOLO detection with confidence threshold
    results = model.predict(frame, conf=0.6)

    annotated_frame = frame.copy()

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])   # class id
            conf = float(box.conf[0])  # confidence
            label = model.names[cls_id]

            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

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

    # Save every nth frame
    if frame_count % 10 == 0:
        out_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(out_path, annotated_frame)
        print(f"✅ Saved {out_path}")

    frame_count += 1

    # Stop after 200 frames
    if frame_count > 200:
        break

cap.release()
print("🎉 Done! Check 'runs/webcam_output/' for saved detections.")
