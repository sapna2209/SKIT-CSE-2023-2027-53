import os
import sqlite3
import tempfile

from db_manager import DatabaseManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class FakeBoxes:                      # mimics result.boxes
    def __init__(self, xyxy, conf):
        self.xyxy, self.conf = xyxy, conf
    def __len__(self):
        return len(self.conf)

class FakeResult:                     # mimics a YOLOv8 Results object
    def __init__(self, boxes, orig_shape):
        self.boxes, self.orig_shape = boxes, orig_shape


# temporary database built from your real schema
tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp.close()
conn = sqlite3.connect(tmp.name)
with open(os.path.join(BASE_DIR, "schema.sql")) as f:
    conn.executescript(f.read())
conn.close()

db = DatabaseManager(tmp.name)
video_id = db.insert_video("test.mp4", fps=30.0, total_frames=900, duration_sec=30.0)

# Test 1: single insert
db.insert_detection(video_id, 120, 4.0, (100, 200, 300, 350), 0.87,
                    frame_image_path="frames/f120.jpg")
assert db.count_detections(video_id) == 1
print("Test 1 passed: single insert")

# Test 2: insert from a YOLO-style result with 2 boxes (frame 1920x1080)
result = FakeResult(FakeBoxes([[100, 100, 200, 200], [500, 400, 900, 700]],
                              [0.91, 0.55]), (1080, 1920))
saved = db.insert_from_yolo_result(video_id, 150, 30.0, result)
assert saved == 2 and db.count_detections(video_id) == 3
print("Test 2 passed: 2 boxes saved from one YOLO result")

# Test 3: values are calculated correctly
row = [r for r in db.fetch_detections(video_id) if r["frame_number"] == 150][0]
assert abs(row["video_time_sec"] - 5.0) < 1e-6          # 150 / 30 fps
assert abs(row["bbox_area_ratio"] - 10000 / (1920 * 1080)) < 1e-9
print("Test 3 passed: video time and box-area ratio are correct")

# Test 4: minimum confidence filter
low = FakeResult(FakeBoxes([[10, 10, 50, 50]], [0.10]), (1080, 1920))
assert db.insert_from_yolo_result(video_id, 200, 30.0, low, min_conf=0.25) == 0
print("Test 4 passed: low-confidence box ignored")

# Test 5: bad data is rejected
for bad in (lambda: db.insert_detection(video_id, 1, 0.0, (0, 0, 10, 10), 1.5),
            lambda: db.insert_detection(video_id, 1, 0.0, (50, 50, 10, 10), 0.5)):
    try:
        bad(); raise SystemExit("FAILED: bad data was accepted")
    except ValueError:
        pass
try:
    db.insert_detection(999, 1, 0.0, (0, 0, 10, 10), 0.5)   # video 999 does not exist
    raise SystemExit("FAILED: unknown video_id was accepted")
except sqlite3.IntegrityError:
    pass
print("Test 5 passed: invalid confidence, invalid box and unknown video rejected")

os.remove(tmp.name)
print("\nAll tests passed.")