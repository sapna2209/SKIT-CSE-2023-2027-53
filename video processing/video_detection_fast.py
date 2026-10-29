"""
video_detection_fast.py  (Sprint 1, Week 12)

Faster version of video_detection.py. It
  1. samples frames at a fixed interval (FR-005) instead of processing every frame,
  2. decodes the video in a background thread while the model is running,
  3. runs YOLOv8 on batches of frames,
  4. saves the annotated image only for frames that contain a pothole (needed for the map popup, FR-003),
  5. writes detections to SQLite in one transaction per batch,
  6. saves structured outputs: detections.csv, detections.jsonl and summary.json (timing + FR-006 check).

Run from the project folder, for example:
    python video_processing/video_detection_fast.py
    python video_processing/video_detection_fast.py --video sample_video.mp4 --interval 30 --conf 0.25
"""
import argparse
import csv
import json
import os
import queue
import sys
import threading
import time

import cv2

# --------------------------------------------------
# 1. Paths and default settings
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")

sys.path.insert(0, DATABASE_DIR)
from db_manager import DatabaseManager  # noqa: E402

MODEL_PATH = os.path.join(PROJECT_ROOT, "best.pt")
VIDEO_PATH = os.path.join(PROJECT_ROOT, "sample_video.mp4")
OUTPUT_ROOT = os.path.join(PROJECT_ROOT, "output")

CONFIDENCE_THRESHOLD = 0.25   # minimum confidence kept (FR-005)
FRAME_INTERVAL = 30           # process every 30th frame (FR-005: 25-30)
BATCH_SIZE = 8                # frames sent to the model together
IMAGE_SIZE = 640              # lower (for example 480) is faster but check accuracy
JPG_QUALITY = 85

FIELDS = ["video_id", "video_name", "frame_number", "video_time_sec", "x_min", "y_min", "x_max", "y_max",
          "bbox_area_ratio", "confidence", "frame_image_path"]


# --------------------------------------------------
# 2. Background frame reader
# --------------------------------------------------
def read_frames(video_path, interval, out_q, batch_size, stats):
    """Decode the video in a thread. Only every `interval`-th frame is fully decoded and sent on."""
    cap = cv2.VideoCapture(video_path)
    batch, idx = [], 0
    try:
        while True:
            if idx % interval == 0:
                ok, frame = cap.read()
                if not ok:
                    break
                batch.append((idx, frame))
                if len(batch) == batch_size:
                    out_q.put(batch)
                    batch = []
            elif not cap.grab():          # skipped frames: grab() avoids the costly colour conversion and copy
                break
            idx += 1
    finally:
        stats["frames_read"] = idx
        if batch:
            out_q.put(batch)
        out_q.put(None)                    # no more frames
        cap.release()


# --------------------------------------------------
# 3. Main processing
# --------------------------------------------------
def process_video(video_path, model, db, out_dir, interval=FRAME_INTERVAL, conf=CONFIDENCE_THRESHOLD,
                  batch_size=BATCH_SIZE, imgsz=IMAGE_SIZE, save_video=False, predict_kwargs=None):
    predict_kwargs = predict_kwargs or {}
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    if fps <= 0:
        fps = 25.0
        print("Warning: could not read FPS, using 25.")
    duration = total_frames / fps if total_frames > 0 else 0.0

    video_name = os.path.basename(video_path)
    video_id = db.insert_video(filename=video_name, fps=fps, total_frames=total_frames, duration_sec=duration)

    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    writer = None
    if save_video:
        writer = cv2.VideoWriter(os.path.join(out_dir, "annotated.mp4"), cv2.VideoWriter_fourcc(*"mp4v"),
                                 max(1.0, fps / interval), (width, height))

    q = queue.Queue(maxsize=4)             # decoding stays up to 4 batches ahead of the model
    stats = {"frames_read": 0}
    threading.Thread(target=read_frames, args=(video_path, interval, q, batch_size, stats), daemon=True).start()

    all_rows, processed = [], 0
    t_wait = t_infer = t_images = t_db = 0.0
    start = time.perf_counter()

    try:
        while True:
            t = time.perf_counter()
            batch = q.get()
            t_wait += time.perf_counter() - t
            if batch is None:
                break

            t = time.perf_counter()
            results = model.predict([f for _, f in batch], imgsz=imgsz, conf=conf, iou=0.45,
                                    verbose=False, **predict_kwargs)
            t_infer += time.perf_counter() - t
            processed += len(batch)

            db_rows = []
            for (idx, frame), res in zip(batch, results):
                boxes = res.boxes
                if boxes is None or len(boxes) == 0:
                    continue
                h, w = res.orig_shape
                t = time.perf_counter()
                annotated = res.plot()
                img_file = os.path.join(frames_dir, f"frame_{idx:06d}.jpg")
                cv2.imwrite(img_file, annotated, [cv2.IMWRITE_JPEG_QUALITY, JPG_QUALITY])
                if writer is not None:
                    writer.write(annotated)
                t_images += time.perf_counter() - t
                rel_path = os.path.relpath(img_file, PROJECT_ROOT).replace("\\", "/")

                for (x1, y1, x2, y2), c in zip(boxes.xyxy.tolist(), boxes.conf.tolist()):
                    if x2 <= x1 or y2 <= y1:
                        continue
                    ratio = (x2 - x1) * (y2 - y1) / (w * h)
                    row = (video_id, idx, round(idx / fps, 3), round(x1, 1), round(y1, 1), round(x2, 1),
                           round(y2, 1), round(ratio, 5), round(float(c), 4), rel_path)
                    db_rows.append(row)
                    all_rows.append(dict(zip(FIELDS, (row[0], video_name) + row[1:])))

            t = time.perf_counter()
            db.insert_detections(db_rows)          # one transaction for the whole batch
            t_db += time.perf_counter() - t
    finally:
        if writer is not None:
            writer.release()

    elapsed = time.perf_counter() - start
    if duration <= 0:                              # frame count was not available in the file header
        duration = stats["frames_read"] / fps

    with open(os.path.join(out_dir, "detections.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=FIELDS)
        wr.writeheader()
        wr.writerows(all_rows)
    with open(os.path.join(out_dir, "detections.jsonl"), "w", encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r) + "\n")

    per_min = elapsed / duration * 60 if duration else None
    summary = {
        "video": video_name, "video_id": video_id, "video_duration_sec": round(duration, 2), "fps": round(fps, 2),
        "frame_interval": interval, "batch_size": batch_size, "imgsz": imgsz, "confidence_threshold": conf,
        "frames_in_video": stats["frames_read"], "frames_processed": processed, "detections_saved": len(all_rows),
        "time_total_sec": round(elapsed, 2), "time_waiting_for_frames_sec": round(t_wait, 2),
        "time_inference_sec": round(t_infer, 2), "time_saving_images_sec": round(t_images, 2),
        "time_database_sec": round(t_db, 2),
        "seconds_per_video_minute": round(per_min, 1) if per_min is not None else None,
        "meets_FR006_(<=120s_per_video_minute)": bool(per_min is not None and per_min <= 120),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


def main():
    ap = argparse.ArgumentParser(description="Detect potholes in a video and save the results.")
    ap.add_argument("--video", default=VIDEO_PATH)
    ap.add_argument("--weights", default=MODEL_PATH)
    ap.add_argument("--interval", type=int, default=FRAME_INTERVAL, help="process every Nth frame")
    ap.add_argument("--conf", type=float, default=CONFIDENCE_THRESHOLD)
    ap.add_argument("--batch", type=int, default=BATCH_SIZE)
    ap.add_argument("--imgsz", type=int, default=IMAGE_SIZE)
    ap.add_argument("--device", default=None, help="for example 0 for the first GPU, or cpu")
    ap.add_argument("--half", action="store_true", help="16-bit inference (GPU only)")
    ap.add_argument("--save-video", action="store_true", help="also write annotated.mp4 (sampled frames)")
    a = ap.parse_args()

    if not os.path.exists(a.weights):
        print("Error: model not found:", a.weights); return
    if not os.path.exists(a.video):
        print("Error: video not found:", a.video); return

    from ultralytics import YOLO               # imported here so the file can be tested without the model
    print("Loading YOLO model...")
    model = YOLO(a.weights)
    kwargs = {}
    if a.device is not None:
        kwargs["device"] = a.device
    if a.half:
        kwargs["half"] = True

    out_dir = os.path.join(OUTPUT_ROOT, os.path.splitext(os.path.basename(a.video))[0])
    summary = process_video(a.video, model, DatabaseManager(), out_dir, a.interval, a.conf, a.batch, a.imgsz,
                            a.save_video, kwargs)

    print("\n------------------------------------")
    print("VIDEO PROCESSING COMPLETED")
    print("------------------------------------")
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("\nOutputs saved in:", out_dir)
    print("Database:", os.path.join(DATABASE_DIR, "potholes.db"))


if __name__ == "__main__":
    main()
