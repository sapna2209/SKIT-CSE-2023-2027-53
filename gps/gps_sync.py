
"""
GPS Video Synchronization Module
--------------------------------
Matches video frames with GPS coordinates
using timestamps and linear interpolation.
"""

import csv
from bisect import bisect_left
from datetime import timedelta, timezone

import cv2


def interpolate_gps(
    gps_points,
    frame_time,
    max_gap_seconds=5.0
):
    """
    Find GPS coordinates corresponding to a frame timestamp.

    Uses linear interpolation between surrounding GPS points.

    Returns:
        Dictionary containing latitude and longitude,
        or None if a reliable match is unavailable.
    """

    if not gps_points:
        return None

    timestamps = [
        point.timestamp
        for point in gps_points
    ]

    index = bisect_left(
        timestamps,
        frame_time
    )

    # Exact timestamp match
    if index < len(gps_points):

        if timestamps[index] == frame_time:

            point = gps_points[index]

            return {
                "latitude": round(point.latitude, 7),
                "longitude": round(point.longitude, 7)
            }

    # No surrounding GPS points
    if index == 0 or index == len(gps_points):
        return None

    previous = gps_points[index - 1]
    following = gps_points[index]

    total_seconds = (
        following.timestamp -
        previous.timestamp
    ).total_seconds()

    # Avoid invalid or large GPS gaps
    if (
        total_seconds <= 0
        or total_seconds > max_gap_seconds
    ):
        return None

    elapsed_seconds = (
        frame_time - previous.timestamp
    ).total_seconds()

    ratio = elapsed_seconds / total_seconds

    # Linear interpolation
    latitude = (
        previous.latitude
        + ratio * (
            following.latitude -
            previous.latitude
        )
    )

    longitude = (
        previous.longitude
        + ratio * (
            following.longitude -
            previous.longitude
        )
    )

    return {
        "latitude": round(latitude, 7),
        "longitude": round(longitude, 7)
    }


def synchronize_video(
    video_path,
    gps_points,
    recording_start_time,
    output_csv="gps_frame_mapping.csv",
    time_offset_seconds=0.0,
    max_gap_seconds=5.0
):
    """
    Synchronize every video frame with GPS coordinates.

    Parameters:
        video_path:
            Path to the input video.

        gps_points:
            List of GPSPoint objects.

        recording_start_time:
            Time when video recording started.
            Must be timezone-aware.

        output_csv:
            CSV output filename.

        time_offset_seconds:
            Optional GPS/video clock adjustment.

        max_gap_seconds:
            Maximum allowed interval between
            surrounding GPS points.

    Returns:
        List of synchronized frame records.
    """

    if recording_start_time.tzinfo is None:
        raise ValueError(
            "Recording start time must include timezone"
        )

    if not gps_points:
        raise ValueError(
            "No GPS points available for synchronization"
        )

    if max_gap_seconds <= 0:
        raise ValueError(
            "max_gap_seconds must be greater than zero"
        )

    # Normalize recording time to UTC
    recording_start_time = (
        recording_start_time.astimezone(timezone.utc)
    )

    # Sort GPS records chronologically
    gps_points = sorted(
        gps_points,
        key=lambda point: point.timestamp
    )

    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise ValueError(
            f"Unable to open video: {video_path}"
        )

    results = []

    try:

        fps = capture.get(cv2.CAP_PROP_FPS)

        total_frames = int(
            capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        if fps <= 0 or total_frames <= 0:
            raise ValueError(
                "Invalid video FPS or frame count"
            )

        for frame_number in range(total_frames):

            # Calculate frame timestamp
            frame_time = (
                recording_start_time
                + timedelta(
                    seconds=(
                        frame_number / fps
                        + time_offset_seconds
                    )
                )
            )

            # Find corresponding GPS location
            location = interpolate_gps(
                gps_points,
                frame_time,
                max_gap_seconds
            )

            results.append({

                "frame_number": frame_number,

                "timestamp": frame_time.isoformat(),

                "latitude": (
                    location["latitude"]
                    if location else None
                ),

                "longitude": (
                    location["longitude"]
                    if location else None
                ),

                "gps_matched": (
                    location is not None
                )
            })

    finally:
        capture.release()

    # Export results to CSV
    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "frame_number",
            "timestamp",
            "latitude",
            "longitude",
            "gps_matched"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    return results
