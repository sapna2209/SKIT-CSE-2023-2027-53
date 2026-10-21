
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "potholes.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 45)
print("       POTHOLE DETECTION SUMMARY")
print("=" * 45)

# Total detections
cursor.execute("SELECT COUNT(*) FROM detections")
total = cursor.fetchone()[0]
print(f"\nTotal detections: {total}")

# Unique frames containing detections
cursor.execute("""
    SELECT COUNT(DISTINCT frame_number)
    FROM detections
""")
frames_with_potholes = cursor.fetchone()[0]
print(f"Frames with detections: {frames_with_potholes}")

# Average confidence
cursor.execute("""
    SELECT AVG(confidence)
    FROM detections
""")
avg_confidence = cursor.fetchone()[0]

if avg_confidence is not None:
    print(f"Average confidence: {avg_confidence * 100:.2f}%")

# Highest number of detections in a frame
cursor.execute("""
    SELECT frame_number, COUNT(*) AS detection_count
    FROM detections
    GROUP BY frame_number
    ORDER BY detection_count DESC, frame_number ASC
    LIMIT 1
""")
result = cursor.fetchone()

if result:
    print(
        f"Frame with most detections: {result[0]} "
        f"({result[1]} detections)"
    )

# Detection counts per frame
cursor.execute("""
    SELECT frame_number, COUNT(*) AS detection_count
    FROM detections
    GROUP BY frame_number
    ORDER BY frame_number
""")
frame_results = cursor.fetchall()

print("\nFirst 10 frame-wise results:")
for frame_number, count in frame_results[:10]:
    print(f"Frame {frame_number}: {count} detections")

print("\n" + "=" * 45)

conn.close()
