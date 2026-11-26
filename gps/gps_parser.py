"""
GPS Parser Module
-----------------
Supports:
1. GPX files (.gpx)
2. NMEA files (.nmea, .log, .txt)

Converts GPS records into a common GPSPoint structure.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import gpxpy
import pynmea2


@dataclass
class GPSPoint:
    """Standard GPS record."""

    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float | None = None


def validate_coordinates(latitude, longitude):
    """Validate GPS latitude and longitude."""

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude")


def parse_gpx(file_path):
    """
    Parse GPS points from a GPX file.

    Returns:
        List of GPSPoint objects.
    """

    points = []

    with open(file_path, "r", encoding="utf-8") as file:
        gpx = gpxpy.parse(file)

    # Read track segments
    for track in gpx.tracks:

        for segment in track.segments:

            for point in segment.points:

                if point.time is None:
                    continue

                timestamp = point.time

                # Ensure timezone-aware timestamp
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(
                        tzinfo=timezone.utc
                    )

                latitude = point.latitude
                longitude = point.longitude

                validate_coordinates(
                    latitude,
                    longitude
                )

                points.append(
                    GPSPoint(
                        timestamp=timestamp.astimezone(
                            timezone.utc
                        ),
                        latitude=latitude,
                        longitude=longitude,
                        altitude=point.elevation
                    )
                )

    return sorted(
        points,
        key=lambda p: p.timestamp
    )


def parse_nmea(file_path):
    """
    Parse NMEA GPS records.

    Uses RMC sentences because they contain:
    - Date
    - Time
    - Latitude
    - Longitude
    """

    points = []

    with open(file_path, "r", encoding="utf-8-sig") as file:

        for line in file:

            line = line.strip()

            if not line.startswith("$"):
                continue

            try:

                message = pynmea2.parse(
                    line,
                    check=("*" in line)
                )

                # Only use RMC sentences
                if message.sentence_type != "RMC":
                    continue

                # Check GPS fix validity
                if message.status != "A":
                    continue

                # RMC contains date and time
                timestamp = datetime.combine(
                    message.datestamp,
                    message.timestamp,
                    tzinfo=timezone.utc
                )

                latitude = message.latitude
                longitude = message.longitude

                validate_coordinates(
                    latitude,
                    longitude
                )

                points.append(
                    GPSPoint(
                        timestamp=timestamp,
                        latitude=latitude,
                        longitude=longitude
                    )
                )

            except (
                pynmea2.ParseError,
                ValueError,
                TypeError,
                AttributeError
            ):
                # Ignore malformed or invalid records
                continue

    return sorted(
        points,
        key=lambda p: p.timestamp
    )


def parse_gps_file(file_path):
    """
    Automatically detect GPS file format.

    Supported extensions:
        .gpx
        .nmea
        .log
        .txt
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".gpx":
        return parse_gpx(file_path)

    elif extension in (".nmea", ".log", ".txt"):
        return parse_nmea(file_path)

    else:
        raise ValueError(
            f"Unsupported GPS file format: {extension}"
        )
