
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "potholes.db")

print("Database path:", DB_PATH)

if not os.path.exists(DB_PATH):
    print("ERROR: Database file not found!")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Display available tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

tables = cursor.fetchall()

print("\nTables in database:")
for table in tables:
    print("-", table[0])

# Display video records
try:
    cursor.execute("SELECT COUNT(*) FROM videos")
    print("\nTotal videos:", cursor.fetchone()[0])

    cursor.execute("""
        SELECT video_id, filename, fps, total_frames, duration_sec
        FROM videos
    """)

    print("\nVideo details:")
    for row in cursor.fetchall():
        print(row)

except sqlite3.Error as e:
    print("Video table error:", e)

# Display detection records
try:
    cursor.execute("SELECT COUNT(*) FROM detections")
    print("\nTotal pothole detections:", cursor.fetchone()[0])

    cursor.execute("""
        SELECT detection_id, video_id, frame_number,
               video_time_sec, confidence
        FROM detections
        LIMIT 10
    """)

    print("\nFirst 10 detections:")
    for row in cursor.fetchall():
        print(row)

except sqlite3.Error as e:
    print("Detection table error:", e)

conn.close()
