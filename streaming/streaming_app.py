import time
import logging
from typing import Dict, Any, List, Optional
from attacks.controller import AttackController
from streaming.transformations import process_batch_events
from streaming.sink import ResultSink
from execution.executor_identity import get_execution_identity

logger = logging.getLogger(__name__)

class SparkByzantineStreamingApp:
    """Orchestrates Spark Structured Streaming pipeline with Byzantine fault injection hooks."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.experiment_id = config.get("experiment", {}).get("id", "default_exp")
        self.attack_controller = AttackController(config)
        self.sink = ResultSink(
            output_dir=config.get("stream", {}).get("output_dir", "output/streaming"),
            experiment_id=self.experiment_id
        )
        self.execution_records: List[Dict[str, Any]] = []

    def run_batch_simulation(self, raw_events: List[Dict[str, Any]], batch_size: int = 2000) -> Dict[str, Any]:
        """Run micro-batch simulation over raw events stream."""
        start_time = time.time()
        logger.info(f"Starting streaming execution for exp '{self.experiment_id}': total input={len(raw_events)}")

        total_batches = (len(raw_events) + batch_size - 1) // batch_size if batch_size > 0 else 1
        all_summaries = []
        total_input = 0
        total_processed = 0
        total_dropped = 0
        total_attacked = 0

        for b_idx in range(total_batches):
            b_start = b_idx * batch_size
            b_events = raw_events[b_start : b_start + batch_size]
            b_time_start = time.time()

            result = process_batch_events(b_events, self.attack_controller)
            b_duration_ms = (time.time() - b_time_start) * 1000.0

            exec_identity = get_execution_identity()
            exec_record = {
                "experiment_id": self.experiment_id,
                "batch_id": b_idx + 1,
                "stage_id": exec_identity.get("stage_id", 1),
                "task_id": exec_identity.get("task_id", b_idx + 1),
                "partition_id": exec_identity.get("partition_id", 0),
                "executor_id": exec_identity.get("executor_id", "executor-1"),
                "hostname": result["sensor_summaries"][0]["executor_hostname"] if result["sensor_summaries"] else exec_identity.get("hostname", "host-1"),
                "duration_ms": b_duration_ms,
                "input_count": result["input_count"],
                "output_count": result["processed_count"],
                "attack_applied": result["attacked_count"] > 0 or result["dropped_count"] > 0,
                "attack_type": self.attack_controller.attack_type
            }
            self.execution_records.append(exec_record)

            self.sink.write_batch_results(b_idx + 1, result["sensor_summaries"])
            all_summaries.extend(result["sensor_summaries"])
            total_input += result["input_count"]
            total_processed += result["processed_count"]
            total_dropped += result["dropped_count"]
            total_attacked += result["attacked_count"]

        total_duration = time.time() - start_time
        self.sink.write_execution_records(self.execution_records)

        # Aggregate overall sensor summaries across micro-batches for ground truth comparison
        overall_sensor_aggs = {}
        for s in all_summaries:
            s_id = s["sensor_id"]
            if s_id not in overall_sensor_aggs:
                overall_sensor_aggs[s_id] = {
                    "sensor_id": s_id,
                    "event_count": 0,
                    "sum_temp_count": 0.0,
                    "min_temp": s["min_temperature"],
                    "max_temp": s["max_temperature"],
                    "sum_hum_count": 0.0,
                    "attack_applied": False,
                    "attack_type": "NONE",
                    "executor_hostname": s.get("executor_hostname", "host-1")
                }
            agg = overall_sensor_aggs[s_id]
            cnt = s["event_count"]
            agg["event_count"] += cnt
            agg["sum_temp_count"] += s["avg_temperature"] * cnt
            agg["min_temp"] = min(agg["min_temp"], s["min_temperature"])
            agg["max_temp"] = max(agg["max_temp"], s["max_temperature"])
            agg["sum_hum_count"] += s["avg_humidity"] * cnt
            if s.get("attack_applied", False):
                agg["attack_applied"] = True
                agg["attack_type"] = s.get("attack_type", "UNKNOWN")

        final_summaries = []
        for s_id, agg in overall_sensor_aggs.items():
            cnt = agg["event_count"]
            final_summaries.append({
                "sensor_id": s_id,
                "event_count": cnt,
                "avg_temperature": round(agg["sum_temp_count"] / cnt, 2) if cnt > 0 else 0.0,
                "min_temperature": round(agg["min_temp"], 2),
                "max_temperature": round(agg["max_temp"], 2),
                "avg_humidity": round(agg["sum_hum_count"] / cnt, 2) if cnt > 0 else 0.0,
                "attack_applied": agg["attack_applied"],
                "attack_type": agg["attack_type"],
                "executor_hostname": agg["executor_hostname"]
            })

        logger.info(f"Streaming execution complete in {total_duration:.2f}s: input={total_input}, processed={total_processed}, dropped={total_dropped}, attacked={total_attacked}")
        return {
            "experiment_id": self.experiment_id,
            "total_duration_sec": total_duration,
            "total_input": total_input,
            "total_processed": total_processed,
            "total_dropped": total_dropped,
            "total_attacked": total_attacked,
            "execution_records": self.execution_records,
            "all_summaries": final_summaries
        }
