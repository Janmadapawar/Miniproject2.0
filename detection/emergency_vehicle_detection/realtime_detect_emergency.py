import sys
from pathlib import Path

# Fix module import issue
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import cv2
import os
import time
from ultralytics import YOLO
from detection.common.alert_system import AlertSystem

# ===============================
# Emergency Vehicle Detection (Enhanced - Non-Emergency View)
# ===============================

# Initialize alert system
alert = AlertSystem()

# Load trained YOLO model
model = YOLO("detection/emergency_vehicle_detection/weights/best.pt")

# Open webcam with optimized settings
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Higher resolution for better detection
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

# Output folder for captured frames
os.makedirs("runs/emergency_webcam_output", exist_ok=True)

frame_count = 0
last_violation = False  # Track detection state
emergency_cooldown = 0  # Prevent alert spam

# ✅ Define emergency vehicle classes (adjust based on your model)
EMERGENCY_CLASSES = ["ambulance", "firetruck", "police car", "fire truck", "police", "emergency"]

print("=" * 60)
print("🚀 Emergency Vehicle Detection Started")
print("=" * 60)
print("🎯 High Accuracy Mode Enabled (Confidence: 0.50)")
print("📦 Display Mode: NON-EMERGENCY Vehicles Only")
print("🚨 Emergency vehicles detected silently with alerts")
print("⌨️  Press 'q' to quit")
print("=" * 60)
print()

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame.")
        break

    # 🔹 Enhanced image preprocessing for better accuracy
    # Increase contrast and brightness
    frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=20)
    
    # Apply slight Gaussian blur to reduce noise
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    
    # Optional: Apply histogram equalization for better low-light performance
    # frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    # frame_yuv[:,:,0] = cv2.equalizeHist(frame_yuv[:,:,0])
    # frame = cv2.cvtColor(frame_yuv, cv2.COLOR_YUV2BGR)

    # Run YOLO detection with HIGHER confidence threshold for accuracy
    results = model(frame, 
                   conf=0.50,           # Higher confidence = fewer false positives
                   iou=0.45,            # Intersection over Union threshold
                   agnostic_nms=True,   # Better non-maximum suppression
                   max_det=15)          # Limit maximum detections
    
    annotated_frame = frame.copy()
    detected_emergency = False
    non_emergency_count = 0
    emergency_vehicle_name = ""

    # Loop through detections
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            label = model.names[cls_id]

            # ✅ Check if it's an emergency vehicle
            is_emergency = any(emer.lower() in label.lower() for emer in EMERGENCY_CLASSES)

            if is_emergency:
                # Emergency vehicle detected (don't show box, but track it)
                detected_emergency = True
                emergency_vehicle_name = label
                print(f"🚨 [Frame {frame_count}] Emergency Vehicle Detected: {label} (Confidence: {conf:.2f})")
            else:
                # 🚫 ONLY show NON-EMERGENCY vehicles
                non_emergency_count += 1
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                
                # Draw thicker bounding box in GREEN for non-emergency
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                
                # Add label with solid background for better visibility
                label_text = f"{label} {conf:.2f}"
                (text_width, text_height), baseline = cv2.getTextSize(
                    label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )
                
                # Draw background rectangle for text
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - text_height - 12),
                    (x1 + text_width + 10, y1),
                    (0, 255, 0),
                    -1
                )
                
                # Draw text in black for contrast
                cv2.putText(
                    annotated_frame,
                    label_text,
                    (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0),
                    2
                )

    # 🚨 Trigger alert for emergency vehicles with cooldown
    if detected_emergency and not last_violation and emergency_cooldown == 0:
        alert.play_alert("emergency_vehicle")
        last_violation = True
        emergency_cooldown = 30  # 30 frame cooldown (~1 second at 30fps)
    elif not detected_emergency:
        last_violation = False
    
    # Decrease cooldown
    if emergency_cooldown > 0:
        emergency_cooldown -= 1

    # ========== UI OVERLAY ==========
    # Create semi-transparent overlay for status bar
    overlay = annotated_frame.copy()
    cv2.rectangle(overlay, (0, 0), (annotated_frame.shape[1], 100), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, annotated_frame, 0.6, 0, annotated_frame)

    # Main status text
    if detected_emergency:
        status_text = f"🚨 EMERGENCY: {emergency_vehicle_name.upper()}"
        status_color = (0, 0, 255)  # Red
    else:
        status_text = "✅ CLEAR - No Emergency Vehicles"
        status_color = (0, 255, 0)  # Green

    cv2.putText(
        annotated_frame,
        status_text,
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        status_color,
        3
    )

    # Vehicle count
    count_text = f"Non-Emergency Vehicles: {non_emergency_count}"
    cv2.putText(
        annotated_frame,
        count_text,
        (10, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # Frame counter in bottom right
    cv2.putText(
        annotated_frame,
        f"Frame: {frame_count}",
        (annotated_frame.shape[1] - 200, annotated_frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    # Display live annotated feed
    cv2.imshow("Emergency Vehicle Detection - Non-Emergency View", annotated_frame)

    # Save every 10th frame
    if frame_count % 10 == 0:
        out_path = f"runs/emergency_webcam_output/frame_{frame_count}.jpg"
        cv2.imwrite(out_path, annotated_frame)

    frame_count += 1

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

print()
print("=" * 60)
print("🎉 Emergency Detection Finished!")
print(f"📊 Total Frames Processed: {frame_count}")
print(f"💾 Output saved to: runs/emergency_webcam_output/")
print("=" * 60)