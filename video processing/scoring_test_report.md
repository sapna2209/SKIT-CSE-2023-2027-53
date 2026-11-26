# Road Scoring - Implementation and Test Report

Project: Smart Pothole Detection System (CSE-S-17)
Sprint 2 - Week 12 (implement scoring function) and Week 13 (test on sample detection data)
Files: `road_scoring.py`, `test_road_scoring.py`

## Week 12 - Scoring function

The function `calculate_road_score(detections)` takes one record per unique pothole
(`confidence`, `bbox_area_ratio`) and returns the score and the road condition.

- Filter: detections with confidence below 0.25 are discarded (FR-005).
- Count severity = min(sum of confidences / 10, 1) x 100
- Size severity = min(confidence-weighted mean box area / 0.02, 1) x 100
- Road score = 0.5 x count severity + 0.5 x size severity (range 0-100)

| Score | Condition |
|---|---|
| 0-20 | Excellent |
| 20-40 | Good |
| 40-60 | Moderate |
| 60-80 | Poor |
| 80-100 | Very Poor |

## Week 13 - Test on sample detection data

Seven sample scenarios, plus tests for confidence weighting, monotonic behaviour,
the 0-100 range (500 random inputs), band boundaries and invalid input.

| Scenario | Count severity | Size severity | Score | Condition |
|---|---|---|---|---|
| No potholes | 0.0 | 0.0 | 0.0 | Excellent |
| All below confidence threshold | 0.0 | 0.0 | 0.0 | Excellent |
| Few small potholes (2) | 18.0 | 25.0 | 21.5 | Good |
| Several medium potholes (5) | 40.0 | 50.0 | 45.0 | Moderate |
| Many medium-large potholes (8) | 68.0 | 75.0 | 71.5 | Poor |
| Severe damage (12) | 100.0 | 100.0 | 100.0 | Very Poor |
| One pothole at exactly 0.25 confidence | 2.5 | 100.0 | 51.25 | Moderate |

Result: all tests passed (see `test_output.txt`).

## Observations
- A higher detection confidence gives a higher score for the same potholes.
- Scores increase with both pothole count and pothole size, and always stay in 0-100.
- The input must contain unique potholes. Per-frame detections from the video pipeline
  must be de-duplicated first; this is planned for the segment-level integration (Week 15).
- One large pothole alone scores 51.25 because size severity saturates at area 0.02.
  The reference values will be refined in Week 14 (thresholds/weights).
