from typing import List, Dict, Any

class GroundTruthCalculator:
    """Independently calculates expected streaming aggregate results from raw input events."""

    @staticmethod
    def calculate_expected_aggregates(raw_events: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Calculate per-sensor expected statistics independently of Spark computation."""
        aggregations: Dict[str, Dict[str, Any]] = {}

        for event in raw_events:
            sensor_id = event["sensor_id"]
            temp = float(event["temperature"])
            hum = float(event["humidity"])

            if sensor_id not in aggregations:
                aggregations[sensor_id] = {
                    "sensor_id": sensor_id,
                    "count": 0,
                    "sum_temp": 0.0,
                    "min_temp": temp,
                    "max_temp": temp,
                    "sum_humidity": 0.0
                }

            agg = aggregations[sensor_id]
            agg["count"] += 1
            agg["sum_temp"] += temp
            agg["min_temp"] = min(agg["min_temp"], temp)
            agg["max_temp"] = max(agg["max_temp"], temp)
            agg["sum_humidity"] += hum

        expected_summaries = {}
        for sensor_id, agg in aggregations.items():
            cnt = agg["count"]
            expected_summaries[sensor_id] = {
                "sensor_id": sensor_id,
                "event_count": cnt,
                "avg_temperature": round(agg["sum_temp"] / cnt, 2) if cnt > 0 else 0.0,
                "min_temperature": round(agg["min_temp"], 2),
                "max_temperature": round(agg["max_temp"], 2),
                "avg_humidity": round(agg["sum_humidity"] / cnt, 2) if cnt > 0 else 0.0
            }

        return expected_summaries
