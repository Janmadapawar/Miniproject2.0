# detection/quick_test.py
import argparse, os, sys
from ultralytics import YOLO
import cv2

parser = argparse.ArgumentParser(description="Quick test YOLO model (image/video/webcam)")
parser.add_argument("--weights", required=True, help="Path to .pt weights")
parser.add_argument("--source", default="bus.jpg", help="Image path, video path, or camera index (0)")
parser.add_argument("--out", default="runs/infer_quick", help="Output folder for annotated images")
parser.add_argument("--conf", type=float, default=0.4)
parser.add_argument("--iou", type=float, default=0.45)
parser.add_argument("--nodisplay", action="store_true", help="Don't open a display window (useful on headless)")
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)

print("Loading model:", args.weights)
model = YOLO(args.weights)
print("Class names:", model.names)

# If source looks like an integer -> webcam
src = args.source
try:
    cam_index = int(src)
    is_cam = True
except Exception:
    is_cam = False

if is_cam:
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Cannot open camera", cam_index); sys.exit(1)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model.predict(source=frame, conf=args.conf, iou=args.iou, verbose=False)
        r = results[0]
        annotated = r.plot()
        annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        if not args.nodisplay:
            cv2.imshow("quick_test", annotated_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
else:
    if os.path.isfile(src) and src.lower().endswith((".jpg", ".jpeg", ".png")):
        img = cv2.imread(src)
        if img is None:
            print("Failed reading image:", src); sys.exit(1)
        results = model.predict(source=img, conf=args.conf, iou=args.iou, verbose=False)
        r = results[0]
        annotated = r.plot()
        annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        out_path = os.path.join(args.out, os.path.basename(src))
        cv2.imwrite(out_path, annotated_bgr)
        print("Saved annotated image to:", out_path)
        if not args.nodisplay:
            cv2.imshow("quick_test", annotated_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("Running model.predict on:", src)
        model.predict(source=src, conf=args.conf, iou=args.iou, save=True)
        print("Predictions are saved under runs/detect or runs/predict.")
