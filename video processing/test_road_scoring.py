"""
test_road_scoring.py

Sprint 2 - Week 13
Tests the road-condition scoring function on sample detection data.
Run:  python test_road_scoring.py
"""
import random
from road_scoring import calculate_road_score, get_road_condition


def make(count, confidence, area):
    """Make `count` sample unique potholes with the same confidence and area."""
    return [{"confidence": confidence, "bbox_area_ratio": area} for _ in range(count)]


# (name, detections, expected score, expected condition)
SCENARIOS = [
    ("No potholes",                    [],                                0.0,  "Excellent"),
    ("All below confidence threshold", make(5, 0.20, 0.03),               0.0,  "Excellent"),
    ("Few small potholes",             make(2, 0.90, 0.005),              21.5, "Good"),
    ("Several medium potholes",        make(5, 0.80, 0.010),              45.0, "Moderate"),
    ("Many medium-large potholes",     make(8, 0.85, 0.015),              71.5, "Poor"),
    ("Severe damage",                  make(12, 0.90, 0.030),             100.0, "Very Poor"),
    ("Confidence exactly 0.25 kept",   make(1, 0.25, 0.02),               51.25, "Moderate"),
]

passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS  {name} {detail}")
    else:
        failed += 1
        print(f"FAIL  {name} {detail}")


print("=" * 70)
print("TEST 1: Sample scenarios")
print("=" * 70)
print(f"{'Scenario':<34}{'Count':>6}{'Size':>8}{'Score':>8}  Condition")
for name, data, exp_score, exp_cond in SCENARIOS:
    r = calculate_road_score(data)
    print(f"{name:<34}{r['count_severity']:>6}{r['size_severity']:>8}{r['road_score']:>8}  {r['road_condition']}")
    check(name, abs(r["road_score"] - exp_score) < 0.01 and r["road_condition"] == exp_cond,
          f"(expected {exp_score}, {exp_cond})")

print("\n" + "=" * 70)
print("TEST 2: Confidence weighting")
print("=" * 70)
high = calculate_road_score(make(6, 0.95, 0.012))["road_score"]
low = calculate_road_score(make(6, 0.40, 0.012))["road_score"]
check("Higher confidence gives a higher score", high > low, f"({high} > {low})")

print("\n" + "=" * 70)
print("TEST 3: Score grows with count and size")
print("=" * 70)
s1 = calculate_road_score(make(2, 0.8, 0.01))["road_score"]
s2 = calculate_road_score(make(6, 0.8, 0.01))["road_score"]
s3 = calculate_road_score(make(6, 0.8, 0.02))["road_score"]
check("More potholes -> higher score", s2 > s1, f"({s2} > {s1})")
check("Larger potholes -> higher score", s3 > s2, f"({s3} > {s2})")

print("\n" + "=" * 70)
print("TEST 4: Score always stays between 0 and 100")
print("=" * 70)
random.seed(1)
ok = True
for _ in range(500):
    data = [{"confidence": random.random(), "bbox_area_ratio": random.random() * 0.2}
            for _ in range(random.randint(0, 40))]
    s = calculate_road_score(data)["road_score"]
    if not 0 <= s <= 100:
        ok = False
check("500 random inputs stay within 0-100", ok)

print("\n" + "=" * 70)
print("TEST 5: Condition band boundaries")
print("=" * 70)
for score, cond in [(0, "Excellent"), (20, "Excellent"), (20.1, "Good"), (40, "Good"),
                    (60, "Moderate"), (80, "Poor"), (80.1, "Very Poor"), (100, "Very Poor")]:
    check(f"score {score} -> {cond}", get_road_condition(score) == cond)

print("\n" + "=" * 70)
print("TEST 6: Invalid input is rejected")
print("=" * 70)
bad_inputs = [
    ("confidence above 1", [{"confidence": 1.5, "bbox_area_ratio": 0.01}]),
    ("negative area",      [{"confidence": 0.8, "bbox_area_ratio": -0.01}]),
]
for name, data in bad_inputs:
    try:
        calculate_road_score(data)
        check(name, False, "(no error raised)")
    except ValueError:
        check(name, True)
try:
    calculate_road_score([], confidence_threshold=2)
    check("threshold above 1", False, "(no error raised)")
except ValueError:
    check("threshold above 1", True)

print("\n" + "=" * 70)
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 70)
