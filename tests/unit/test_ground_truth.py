import pytest
from ground_truth.calculator import GroundTruthCalculator
from ground_truth.comparator import GroundTruthComparator
from ground_truth.validator import GroundTruthValidator

def test_ground_truth_calculation():
    raw_events = [
        {"sensor_id": "S001", "temperature": 30.0, "humidity": 50.0},
        {"sensor_id": "S001", "temperature": 40.0, "humidity": 60.0},
        {"sensor_id": "S002", "temperature": 20.0, "humidity": 40.0}
    ]
    expected = GroundTruthCalculator.calculate_expected_aggregates(raw_events)

    assert "S001" in expected
    assert expected["S001"]["event_count"] == 2
    assert expected["S001"]["avg_temperature"] == 35.0
    assert expected["S001"]["min_temperature"] == 30.0
    assert expected["S001"]["max_temperature"] == 40.0

def test_ground_truth_validator_pass():
    raw_events = [
        {"sensor_id": "S001", "temperature": 30.0, "humidity": 50.0},
        {"sensor_id": "S001", "temperature": 40.0, "humidity": 60.0}
    ]
    actual_summaries = [
        {"sensor_id": "S001", "event_count": 2, "avg_temperature": 35.0, "min_temperature": 30.0, "max_temperature": 40.0, "avg_humidity": 55.0}
    ]
    validator = GroundTruthValidator(tolerance=0.01)
    res = validator.validate(raw_events, actual_summaries)

    assert res["correct_items"] == 1
    assert res["incorrect_items"] == 0
    assert res["accuracy_rate"] == 1.0

def test_ground_truth_validator_corruption_fail():
    raw_events = [
        {"sensor_id": "S001", "temperature": 30.0, "humidity": 50.0},
        {"sensor_id": "S001", "temperature": 40.0, "humidity": 60.0}
    ]
    actual_summaries = [
        {"sensor_id": "S001", "event_count": 2, "avg_temperature": 85.0, "min_temperature": 30.0, "max_temperature": 40.0, "avg_humidity": 55.0}
    ]
    validator = GroundTruthValidator(tolerance=0.01)
    res = validator.validate(raw_events, actual_summaries)

    assert res["correct_items"] == 0
    assert res["incorrect_items"] == 1
    assert res["accuracy_rate"] == 0.0
