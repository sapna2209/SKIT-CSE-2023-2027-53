PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS videos (
    video_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        TEXT NOT NULL,
    fps             REAL,
    total_frames    INTEGER,
    duration_sec    REAL,
    recording_start TEXT,
    uploaded_at     TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS road_segments (
    segment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id        INTEGER NOT NULL,
    segment_index   INTEGER NOT NULL,
    start_lat       REAL,
    start_lon       REAL,
    end_lat         REAL,
    end_lon         REAL,
    pothole_count   INTEGER DEFAULT 0,
    road_score      REAL,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS detections (
    detection_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id         INTEGER NOT NULL,
    frame_number     INTEGER NOT NULL,
    video_time_sec   REAL NOT NULL,
    x_min            REAL NOT NULL,
    y_min            REAL NOT NULL,
    x_max            REAL NOT NULL,
    y_max            REAL NOT NULL,
    bbox_area_ratio  REAL,
    confidence       REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    frame_image_path TEXT,
    latitude         REAL,
    longitude        REAL,
    segment_id       INTEGER,
    detected_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id)   REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (segment_id) REFERENCES road_segments(segment_id)
);

CREATE TABLE IF NOT EXISTS gps_points (
    gps_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id        INTEGER NOT NULL,
    video_time_sec  REAL NOT NULL,
    latitude        REAL NOT NULL,
    longitude       REAL NOT NULL,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_det_video ON detections(video_id);
CREATE INDEX IF NOT EXISTS idx_det_time  ON detections(video_id, video_time_sec);
CREATE INDEX IF NOT EXISTS idx_gps_time  ON gps_points(video_id, video_time_sec);