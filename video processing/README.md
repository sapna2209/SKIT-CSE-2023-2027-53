# Sprint 1: Video Processing Pipeline

## Overview
This module processes road videos to identify potholes using OpenCV and a trained YOLOv8 model.

## Implemented Features
- Extract video frames using OpenCV.
- Read video properties such as FPS, frame count, duration, and resolution.
- Test the processing pipeline on multiple road videos.
- Run YOLOv8 inference on video frames.
- Draw bounding boxes around detected potholes.
- Generate an annotated output video.
- Store video metadata and pothole detection records in SQLite.
- Verify stored records and generate a detection summary.
- Export database tables to CSV for readable inspection.

## Main Files
- `video_processor.py` — extracts frames from videos.
- `video_detection.py` — runs YOLOv8 inference and saves annotated video output and detection records.
- `check_database.py` — verifies database tables and records.
- `detection_summary.py` — generates detection statistics.
- `export_database.py` — exports database tables to CSV.
- `create_db.py` — initializes the SQLite database.
- `schema.sql` — defines the database schema.
- `db_manager.py` — manages database operations.

## Current Test
The pipeline was tested using a sample road video.

- Input video: `sample_video.mp4`
- Video FPS: 25
- Total frames: 375
- Duration: 15 seconds
- Detection records stored: 3,206

These results represent the current test run and are not a measure of unique potholes or model accuracy.

## Running the Pipeline
1. Install the required Python dependencies.
2. Place the trained YOLO model and input video in the configured locations.
3. Initialize the SQLite database if necessary.
4. Run `video_processor.py` to extract frames.
5. Run `video_detection.py` to detect potholes and generate annotated output.
6. Run `check_database.py` to verify stored records.
7. Run `detection_summary.py` to view detection statistics.

## Sprint Progress
- Week 7: Frame extraction implemented.
- Week 8: Multiple-video testing performed.
- Week 9: YOLOv8 inference integrated into video processing.
