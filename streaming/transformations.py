import socket
import logging
from typing import List, Dict, Any, Optional
from attacks.controller import AttackController

logger = logging.getLogger(__name__)

def process_batch_events(events: List[Dict[str, Any]], attack_controller: AttackController) -> Dict[str, Any]:
    """Process a micro-batch of events with deterministic aggregation and attack controller application."""
    hostname = socket.gethostname()
    processed_records = []
    dropped_count = 0
    attacked_count = 0

    for event in events:
        # Apply attack controller to event before/during processing
        attacked_event = attack_controller.process_record(event, hostname=hostname)
        
        if attacked_event.get("dropped", False):
            dropped_count += 1
            continue

        if attacked_event.get("attack_applied", False):
            attacked_count += 1

        processed_records.append(attacked_event)

    # Deterministic Aggregation per sensor_id
    aggregations: Dict[str, Dict[str, Any]] = {}
    for rec in processed_records:
        sensor_id = rec.get("sensor_id", "UNKNOWN")
        temp = float(rec.get("temperature", 0.0))
        hum = float(rec.get("humidity", 0.0))

        if sensor_id not in aggregations:
            aggregations[sensor_id] = {
                "sensor_id": sensor_id,
                "count": 0,
                "sum_temp": 0.0,
                "min_temp": temp,
                "max_temp": temp,
                "sum_humidity": 0.0,
                "attack_applied": False,
                "attack_type": "NONE"
            }

        agg = aggregations[sensor_id]
        agg["count"] += 1
        agg["sum_temp"] += temp
        agg["min_temp"] = min(agg["min_temp"], temp)
        agg["max_temp"] = max(agg["max_temp"], temp)
        agg["sum_humidity"] += hum
        if rec.get("attack_applied", False):
            agg["attack_applied"] = True
            agg["attack_type"] = rec.get("attack_type", "UNKNOWN")

    # Format final aggregation dictionary output
    sensor_summaries = []
    for s_id, agg in aggregations.items():
        count = agg["count"]
        avg_temp = round(agg["sum_temp"] / count, 2) if count > 0 else 0.0
        avg_hum = round(agg["sum_humidity"] / count, 2) if count > 0 else 0.0
        
        summary = {
            "sensor_id": s_id,
            "event_count": count,
            "avg_temperature": avg_temp,
            "min_temperature": round(agg["min_temp"], 2),
            "max_temperature": round(agg["max_temp"], 2),
            "avg_humidity": avg_hum,
            "attack_applied": agg["attack_applied"],
            "attack_type": agg["attack_type"],
            "executor_hostname": hostname
        }

        # If attack_type is WRONG_AGGREGATION and target matched at aggregation level
        if attack_controller.attack_type == "WRONG_AGGREGATION" and attack_controller.should_attack(hostname):
            summary = attack_controller.attack_instance.apply(summary, {"hostname": hostname})

        sensor_summaries.append(summary)

    return {
        "sensor_summaries": sensor_summaries,
        "input_count": len(events),
        "processed_count": len(processed_records),
        "dropped_count": dropped_count,
        "attacked_count": attacked_count
    }
