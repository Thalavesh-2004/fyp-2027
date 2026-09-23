import numpy as np
from typing import List, Dict, Any

class ExperimentMetricsCalculator:
    """Calculates quantitative performance, latency, and correctness metrics."""

    @staticmethod
    def compute_metrics(experiment_id: str,
                        streaming_result: Dict[str, Any],
                        validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compute complete summary metrics from execution and validation results."""
        duration_sec = streaming_result.get("total_duration_sec", 1.0)
        if duration_sec <= 0:
            duration_sec = 1.0

        total_input = streaming_result.get("total_input", 0)
        total_output = streaming_result.get("total_processed", 0)
        throughput = total_input / duration_sec

        execution_records = streaming_result.get("execution_records", [])
        durations = [r["duration_ms"] for r in execution_records if "duration_ms" in r]
        
        avg_latency = float(np.mean(durations)) if durations else 0.0
        p95_latency = float(np.percentile(durations, 95)) if durations else 0.0

        correct_results = validation_result.get("correct_items", 0)
        incorrect_results = validation_result.get("incorrect_items", 0)
        total_validated = validation_result.get("total_items", 0)
        corruption_rate = validation_result.get("corruption_rate", 0.0)

        attack_attempts = streaming_result.get("total_attacked", 0) + streaming_result.get("total_dropped", 0)
        successful_attacks = incorrect_results + streaming_result.get("total_dropped", 0)

        return {
            "experiment_id": experiment_id,
            "total_input_records": total_input,
            "total_output_records": total_output,
            "correct_results": correct_results,
            "incorrect_results": incorrect_results,
            "attack_attempts": attack_attempts,
            "successful_attacks": successful_attacks,
            "corruption_rate": round(corruption_rate, 4),
            "throughput_records_per_second": round(throughput, 2),
            "average_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "total_processing_time_ms": round(duration_sec * 1000.0, 2)
        }
