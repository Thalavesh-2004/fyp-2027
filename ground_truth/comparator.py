import math
from typing import Dict, Any, List

class GroundTruthComparator:
    """Compares Spark output records against independent ground truth."""

    def __init__(self, tolerance: float = 0.01):
        self.tolerance = tolerance

    def compare_summaries(self, actual_summaries: List[Dict[str, Any]],
                          expected_summaries: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare actual streaming summaries vs expected ground-truth statistics."""
        comparison_results = []

        actual_map = {item["sensor_id"]: item for item in actual_summaries}
        all_sensor_ids = set(actual_map.keys()).union(set(expected_summaries.keys()))

        for sensor_id in sorted(all_sensor_ids):
            actual = actual_map.get(sensor_id, {})
            expected = expected_summaries.get(sensor_id, {})

            actual_avg_temp = float(actual.get("avg_temperature", 0.0)) if actual else 0.0
            expected_avg_temp = float(expected.get("avg_temperature", 0.0)) if expected else 0.0

            abs_err = abs(actual_avg_temp - expected_avg_temp)
            rel_err = abs_err / abs(expected_avg_temp) if expected_avg_temp != 0 else (0.0 if abs_err == 0 else 1.0)
            is_correct = abs_err <= self.tolerance and actual.get("event_count", 0) == expected.get("event_count", 0)

            comparison_results.append({
                "sensor_id": sensor_id,
                "expected_event_count": expected.get("event_count", 0),
                "actual_event_count": actual.get("event_count", 0),
                "expected_avg_temp": expected_avg_temp,
                "actual_avg_temp": actual_avg_temp,
                "absolute_error": round(abs_err, 4),
                "relative_error": round(rel_err, 4),
                "is_correct": is_correct,
                "attack_applied": actual.get("attack_applied", False),
                "attack_type": actual.get("attack_type", "NONE")
            })

        return comparison_results
