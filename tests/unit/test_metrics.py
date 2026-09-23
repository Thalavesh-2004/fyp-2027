import pytest
from experiments.metrics import ExperimentMetricsCalculator

def test_metrics_calculation():
    streaming_res = {
        "total_duration_sec": 10.0,
        "total_input": 1000,
        "total_processed": 1000,
        "total_dropped": 0,
        "total_attacked": 50,
        "execution_records": [{"duration_ms": 100.0}, {"duration_ms": 200.0}]
    }
    validation_res = {
        "total_items": 5,
        "correct_items": 4,
        "incorrect_items": 1,
        "corruption_rate": 0.20
    }

    metrics = ExperimentMetricsCalculator.compute_metrics("exp_test", streaming_res, validation_res)

    assert metrics["experiment_id"] == "exp_test"
    assert metrics["total_input_records"] == 1000
    assert metrics["throughput_records_per_second"] == 100.0
    assert metrics["correct_results"] == 4
    assert metrics["incorrect_results"] == 1
    assert metrics["corruption_rate"] == 0.20
    assert metrics["average_latency_ms"] == 150.0
