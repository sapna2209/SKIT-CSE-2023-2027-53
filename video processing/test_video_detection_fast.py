"""Tests the logic of video_detection_fast.py with a fake model (no best.pt needed)."""
import csv, json, os, shutil, sqlite3, sys, tempfile
import cv2, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import video_detection_fast as vd
from db_manager import DatabaseManager

tmp = tempfile.mkdtemp()
video = os.path.join(tmp, "t.mp4")
vw = cv2.VideoWriter(video, cv2.VideoWriter_fourcc(*"mp4v"), 25, (640, 480))
for i in range(375):                                   # 15 s at 25 fps, like the sample video
    f = np.full((480, 640, 3), 90, np.uint8); cv2.rectangle(f, (i % 300, 100), (i % 300 + 80, 180), (30, 30, 30), -1); vw.write(f)
vw.release()

class B:
    def __init__(s, xyxy, conf): s.xyxy, s.conf = np.array(xyxy, float).reshape(-1, 4), np.array(conf, float)
    def __len__(s): return len(s.conf)
class R:
    def __init__(s, frame, boxes): s.boxes, s.orig_shape, s._f = boxes, frame.shape[:2], frame
    def plot(s): return s._f.copy()
class Fake:
    def __init__(s): s.batches = []
    def predict(s, frames, **kw):
        s.batches.append(len(frames)); out = []
        for fr in frames:
            ys, xs = np.where(fr[:, :, 0] < 50)
            ok = len(xs) and xs.max() < 320
            out.append(R(fr, B([[xs.min(), ys.min(), xs.max(), ys.max()]], [0.8]) if ok else B([], [])))
        return out

db_path = os.path.join(tmp, "p.db")
c = sqlite3.connect(db_path); c.executescript(open(os.path.join(HERE, "..", "database", "schema.sql")).read()); c.close()
db = DatabaseManager(db_path)
model = Fake()
out = os.path.join(tmp, "out")
s = vd.process_video(video, model, db, out, interval=30, batch_size=4, save_video=True)
print(json.dumps(s, indent=1))

assert s["frames_in_video"] == 375 and s["frames_processed"] == 13          # frames 0,30,...,360
assert model.batches == [4, 4, 4, 1]
rows = list(csv.DictReader(open(os.path.join(out, "detections.csv"))))
jl = [json.loads(l) for l in open(os.path.join(out, "detections.jsonl"))]
assert len(rows) == len(jl) == s["detections_saved"] == db.count_detections(s["video_id"]) > 0
d = db.fetch_detections(s["video_id"])[0]
assert abs(d["video_time_sec"] - d["frame_number"] / 25) < 1e-3 and 0 <= d["confidence"] <= 1
assert all(os.path.exists(os.path.join(out, "frames", f"frame_{int(r['frame_number']):06d}.jpg")) for r in rows)
assert os.path.exists(os.path.join(out, "annotated.mp4")) and os.path.exists(os.path.join(out, "summary.json"))
print("ALL TESTS PASSED")
shutil.rmtree(tmp)
