"""
road_scoring.py

Sprint 2 - Week 13
Initial image-based road-condition scoring module.

Important:
- Input records must represent UNIQUE potholes, not every frame detection.
- bbox_area_ratio is bounding-box area / full frame area.
- The score is a prototype severity indicator, not an engineering road-safety rating.
"""

CONFIDENCE_THRESHOLD = 0.25
REFERENCE_POTHOLE_COUNT = 10
REFERENCE_AVERAGE_AREA_RATIO = 0.02

COUNT_WEIGHT = 0.50
SIZE_WEIGHT = 0.50


def filter_detections(detections, confidence_threshold=CONFIDENCE_THRESHOLD):
    """
    Keep valid detections that meet the confidence threshold.

    Each detection must contain:
        confidence
        bbox_area_ratio

    The caller must supply one representative record per unique pothole.
    """
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1")

    valid_detections = []

    for detection in detections:
        confidence = float(detection["confidence"])
        area_ratio = float(detection["bbox_area_ratio"])

        if not 0 <= confidence <= 1:
            raise ValueError("Detection confidence must be between 0 and 1")

        if area_ratio < 0:
            raise ValueError("bbox_area_ratio cannot be negative")

        if confidence >= confidence_threshold:
            valid_detections.append(detection)

    return valid_detections

def calculate_count_severity(detections, reference_count=REFERENCE_POTHOLE_COUNT):
    weighted = sum(float(d["confidence"]) for d in detections)
    return min(weighted / reference_count, 1.0) * 100

def calculate_size_severity(detections, reference_average_area=REFERENCE_AVERAGE_AREA_RATIO):
    total_conf = sum(float(d["confidence"]) for d in detections)
    if total_conf == 0:
        return 0.0
    avg_area = sum(float(d["confidence"]) * float(d["bbox_area_ratio"]) for d in detections) / total_conf
    return min(avg_area / reference_average_area, 1.0) * 100

def get_road_condition(score):
    """Convert a severity score into a condition category."""
    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")

    if score <= 20:
        return "Excellent"
    if score <= 40:
        return "Good"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "Poor"
    return "Very Poor"


def calculate_road_score(
    detections,
    confidence_threshold=CONFIDENCE_THRESHOLD,
    reference_count=REFERENCE_POTHOLE_COUNT,
    reference_average_area=REFERENCE_AVERAGE_AREA_RATIO
):
    """
    Calculate the road-condition severity score.

    detections: one representative dictionary per unique pothole.
    Returns a dictionary containing the score and intermediate values.
    """
    valid_detections = filter_detections(
        detections,
        confidence_threshold
    )

    pothole_count = len(valid_detections)

    count_severity = calculate_count_severity(valid_detections, reference_count)

    size_severity = calculate_size_severity(
        valid_detections,
        reference_average_area
    )

    road_score = (
        COUNT_WEIGHT * count_severity
        + SIZE_WEIGHT * size_severity
    )

    return {
        "pothole_count": pothole_count,
        "count_severity": round(count_severity, 2),
        "size_severity": round(size_severity, 2),
        "road_score": round(road_score, 2),
        "road_condition": get_road_condition(road_score)
    }


if __name__ == "__main__":
    # Sample data: these records represent four UNIQUE potholes.
    sample_detections = [
        {"confidence": 0.90, "bbox_area_ratio": 0.020},
        {"confidence": 0.80, "bbox_area_ratio": 0.030},
        {"confidence": 0.75, "bbox_area_ratio": 0.015},
        {"confidence": 0.85, "bbox_area_ratio": 0.025},
        {"confidence": 0.20, "bbox_area_ratio": 0.040},  # filtered out
    ]

    result = calculate_road_score(sample_detections)

    print("ROAD CONDITION SCORING RESULT")
    print("-" * 35)

    for key, value in result.items():
        print(f"{key}: {value}")
