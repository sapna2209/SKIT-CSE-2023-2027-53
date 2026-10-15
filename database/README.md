# Smart Pothole Detection System – Database Module

## Overview

This module manages the database for the Smart Pothole Detection System. It uses **SQLite** to store video metadata, road segment information, pothole detections, and GPS coordinates collected during road video analysis.

The database provides a structured way to store detection results for further analysis, road condition assessment, and pothole location tracking.

## Project Files

```text
database/
├── create_db.py
├── schema.sql
├── potholes.db
└── README.md
```

| File | Description |
|---|---|
| `create_db.py` | Python script that creates and initializes the SQLite database using the SQL schema. |
| `schema.sql` | Defines the database tables, relationships, constraints, and indexes. |
| `potholes.db` | SQLite database file containing the tables and stored records. It is created when the script runs. |
| `README.md` | Documents the database module and its usage. |

## Technologies Used

- **Python** – Database initialization script.
- **SQLite3** – Lightweight relational database.
- **SQL** – Table definitions, foreign keys, constraints, and indexes.

## Database Schema

The database contains four tables.

### 1. `videos`

Stores metadata about uploaded road videos.

| Column | Description |
|---|---|
| `video_id` | Primary key; uniquely identifies each video. |
| `filename` | Name of the uploaded video. |
| `fps` | Frames per second. |
| `total_frames` | Total number of frames in the video. |
| `duration_sec` | Video duration in seconds. |
| `recording_start` | Recording start time. |
| `uploaded_at` | Timestamp when the record is created. |

### 2. `road_segments`

Stores information about road segments associated with a video.

| Column | Description |
|---|---|
| `segment_id` | Primary key; uniquely identifies a road segment. |
| `video_id` | References the associated video. |
| `segment_index` | Segment sequence number within the video. |
| `start_lat`, `start_lon` | Starting GPS coordinates. |
| `end_lat`, `end_lon` | Ending GPS coordinates. |
| `pothole_count` | Number of potholes associated with the segment. |
| `road_score` | Score representing the road condition. |

### 3. `detections`

Stores pothole detection results for individual video frames.

| Column | Description |
|---|---|
| `detection_id` | Primary key for each detection. |
| `video_id` | References the video in which the pothole was detected. |
| `frame_number` | Frame containing the detection. |
| `video_time_sec` | Timestamp of the frame within the video. |
| `x_min`, `y_min`, `x_max`, `y_max` | Bounding box coordinates of the detected pothole. |
| `bbox_area_ratio` | Ratio of the bounding box area to the frame area. |
| `confidence` | Model confidence score between 0 and 1. |
| `frame_image_path` | Path to the corresponding frame image, if available. |
| `latitude`, `longitude` | GPS coordinates associated with the detection. |
| `segment_id` | References the corresponding road segment, if assigned. |
| `detected_at` | Timestamp when the record is created. |

### 4. `gps_points`

Stores GPS coordinates associated with video timestamps.

| Column | Description |
|---|---|
| `gps_id` | Primary key for each GPS record. |
| `video_id` | References the associated video. |
| `video_time_sec` | Timestamp within the video. |
| `latitude` | GPS latitude. |
| `longitude` | GPS longitude. |

## Database Relationships

- One video can have multiple road segments.
- One video can have multiple pothole detections.
- One video can have multiple GPS points.
- A road segment can be associated with multiple detections.

Foreign keys connect related records and maintain referential integrity. The schema enables foreign-key enforcement on the SQLite connection that executes it.

## Indexes and Constraints

The schema includes:

- **Primary keys** to uniquely identify records.
- **Foreign keys** to connect related tables.
- **Confidence constraint** to ensure detection confidence remains between `0` and `1`.
- **Cascade deletion** so deleting a video also deletes its associated road segments, detections, and GPS points.
- **Indexes** on video IDs and video timestamps to improve common lookup queries.

## Setup and Usage

### Prerequisites

- Python 3.x
- SQLite3, included with Python's standard library.

No additional Python packages are required.

### Step 1: Keep the files together

Ensure `create_db.py` and `schema.sql` are in the same directory. The database file will be created in that directory.

### Step 2: Create the database

Open a terminal in the database directory and run:

```bash
python create_db.py
```

On successful execution, the script prints the location of `potholes.db`.

### Step 3: Verify the database

You can inspect the tables using Python:

```python
import sqlite3

conn = sqlite3.connect("potholes.db")

cursor = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

for row in cursor.fetchall():
    print(row[0])

conn.close()
```

Expected tables:

```text
videos
sqlite_sequence
road_segments
detections
gps_points
```

`sqlite_sequence` is an internal SQLite table used to track `AUTOINCREMENT` values.

## Notes

- `create_db.py` uses paths relative to its own location, so it can be executed from another working directory.
- The schema uses `CREATE TABLE IF NOT EXISTS`, allowing the initialization script to run again without recreating existing tables.
- Running the script again does not reset or delete existing records.
- `potholes.db` is a binary SQLite database file; it should not be edited as a text file.
- The schema defines the database structure, but application code must insert video metadata, detections, GPS points, and road segment information.

## Future Integration

This database module can be integrated with the pothole detection pipeline to store model predictions, associate detections with GPS coordinates, organize road segments, and support road condition analysis through a web dashboard.

## Author

Smart Pothole Detection System – Database Module  
Developed as part of the project for road condition monitoring and pothole detection.
