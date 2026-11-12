# GPS Log Format Study and Parsing Plan

Project: Smart Pothole Detection System (CSE-S-17)
Sprint 2, Week 13 - Member 1 (Sanyam Singh)
Related requirements: FR-002 (GPS log parsed from Excel), NFR-002 (error handling), NFR-003 (modular code)

## 1. Purpose
Each road video is recorded together with a GPS log exported from a smartphone recording app as an Excel file.
To place a detected pothole on the map, we match the video time of the detection to a GPS point.
This document records the expected log format and the plan for parsing it.

## 2. Expected Excel GPS log format
Based on typical smartphone GPS-logger exports. If the real app export differs, only the column-name mapping in Section 4 changes.

| Column | Type | Required | Description |
|---|---|---|---|
| Timestamp | Excel datetime | Yes | Time of the GPS fix, with date |
| Latitude | float (degrees) | Yes | -90 to 90 |
| Longitude | float (degrees) | Yes | -180 to 180 |
| Altitude_m | float | No | Not used by the system |
| Speed_mps | float | No | Can be used to check data quality |
| Accuracy_m | float | No | Can be used to drop poor fixes |

- Sampling rate: about 1 fix per second (a 15 s video gives about 15 rows).
- One sheet, with the header in row 1.
- A synthetic example is in `sample_gps_log.xlsx` (not real data).

## 3. How the log connects to our database
Existing table in `potholes.db`:

    gps_points(gps_id, video_id, video_time_sec, latitude, longitude)

Observed state of the database: `gps_points` is empty, and `videos.recording_start` is NULL for all videos.
`recording_start` is needed to convert GPS timestamps to video time.

## 4. Parsing plan
1. **Read**: `pandas.read_excel(path, engine="openpyxl")`.
2. **Standardise columns**: map the app's names to `timestamp`, `latitude`, `longitude` (case-insensitive). If a required column is missing, stop with a clear error message.
3. **Clean**:
   - convert `timestamp` to datetime; drop rows that fail
   - drop rows with empty latitude or longitude
   - drop rows outside valid coordinate ranges
   - remove duplicate timestamps and sort by time
   - optionally drop rows with Accuracy_m above a limit (for example 30 m)
4. **Find `recording_start`** (in this order of preference):
   1. video creation time from file metadata
   2. first GPS timestamp
   3. a value entered by the user in the dashboard
5. **Convert to video time**: `video_time_sec = (timestamp - recording_start).total_seconds()`. Keep rows from 0 to the video duration.
6. **Store**: insert into `gps_points` for the matching `video_id`, in one transaction (same style as `db_manager.py`, with a new `insert_gps_points()` method).
7. **Matching (Week 15)**: for each detection, find the GPS point with the nearest `video_time_sec`.

## 5. Planned function layout (module: `gps_parser.py`)

    load_gps_log(path)                    -> raw DataFrame
    clean_gps_log(df)                     -> DataFrame[timestamp, latitude, longitude]
    to_video_time(df, recording_start)    -> DataFrame[video_time_sec, latitude, longitude]
    save_gps_points(video_id, df)         -> number of rows saved

## 6. Error handling (NFR-002)
| Problem | Action |
|---|---|
| File not found or not .xlsx | Show an error; do not continue |
| Required column missing | Show which column is missing |
| Empty sheet or no valid rows | Show an error |
| Gap of more than 2 s between fixes | Warn; handle by interpolation in Week 17 |
| GPS time range does not overlap the video | Warn that the log does not match the video |

## 7. Open points
- Confirm the exact column names and timestamp time zone with a real export from the recording app.
- Decide the source of `recording_start`.

## 8. Next step
Week 14: implement `gps_parser.py` using this plan.
