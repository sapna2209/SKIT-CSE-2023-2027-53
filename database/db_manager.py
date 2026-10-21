import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(BASE_DIR, "potholes.db")


def _to_list(x):
    """Works for YOLO tensors (.tolist) and plain Python lists."""
    return x.tolist() if hasattr(x, "tolist") else list(x)


class DatabaseManager:
    def __init__(self, db_path=DEFAULT_DB):
        self.db_path = db_path

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------- videos ----------
    def insert_video(self, filename, fps=None, total_frames=None,
                     duration_sec=None, recording_start=None):
        """Save one uploaded video and return its video_id."""
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO videos
                   (filename, fps, total_frames, duration_sec, recording_start)
                   VALUES (?, ?, ?, ?, ?)""",
                (filename, fps, total_frames, duration_sec, recording_start))
            return cur.lastrowid

    # ---------- detections ----------
    def insert_detection(self, video_id, frame_number, video_time_sec, bbox,
                         confidence, bbox_area_ratio=None, frame_image_path=None):
        """Save one detection. bbox = (x_min, y_min, x_max, y_max) in pixels."""
        return self.insert_detections([self._make_row(
            video_id, frame_number, video_time_sec, bbox,
            confidence, bbox_area_ratio, frame_image_path)])

    def insert_detections(self, rows):
        """Save many detections in one transaction (fast). Returns count saved."""
        if not rows:
            return 0
        with self._connect() as conn:
            conn.executemany(
                """INSERT INTO detections
                   (video_id, frame_number, video_time_sec,
                    x_min, y_min, x_max, y_max,
                    bbox_area_ratio, confidence, frame_image_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", rows)
        return len(rows)

    def insert_from_yolo_result(self, video_id, frame_number, fps, result,
                                frame_image_path=None, min_conf=0.0):
        """Save every box of one YOLOv8 result (one frame). Returns count saved.

        result = model(frame)[0]   # Ultralytics Results object
        """
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return 0
        height, width = result.orig_shape
        video_time = frame_number / fps if fps else 0.0

        rows = []
        for (x1, y1, x2, y2), conf in zip(_to_list(boxes.xyxy), _to_list(boxes.conf)):
            if conf < min_conf:
                continue
            area_ratio = (max(0, x2 - x1) * max(0, y2 - y1)) / (width * height)
            rows.append(self._make_row(video_id, frame_number, video_time,
                                       (x1, y1, x2, y2), conf,
                                       area_ratio, frame_image_path))
        return self.insert_detections(rows)

    @staticmethod
    def _make_row(video_id, frame_number, video_time_sec, bbox,
                  confidence, bbox_area_ratio, frame_image_path):
        x1, y1, x2, y2 = bbox
        if not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(f"confidence must be between 0 and 1, got {confidence}")
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"invalid bounding box: {bbox}")
        return (video_id, int(frame_number), float(video_time_sec),
                float(x1), float(y1), float(x2), float(y2),
                None if bbox_area_ratio is None else float(bbox_area_ratio),
                float(confidence), frame_image_path)

    # ---------- reading back ----------
    def fetch_detections(self, video_id):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM detections WHERE video_id = ? ORDER BY video_time_sec",
                (video_id,)).fetchall()
        return [dict(r) for r in rows]

    def count_detections(self, video_id):
        with self._connect() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM detections WHERE video_id = ?",
                (video_id,)).fetchone()[0]