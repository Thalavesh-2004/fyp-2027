import pytest
import os
from pathlib import Path
from experiments.experiment_manager import ExperimentManager

def test_full_experiment_pipeline():
    config_path = "config/baseline.yaml"
    manager = ExperimentManager(config_path)
    summary = manager.run()

    assert summary["experiment_id"] == "exp_baseline_00"
    assert summary["total_input_records"] == 10000
    assert summary["corruption_rate"] == 0.0

    exp_dir = Path("output/experiment_results/exp_baseline_00")
    assert exp_dir.exists()
    assert (exp_dir / "metrics.json").exists()
    assert (exp_dir / "summary.json").exists()
    assert (exp_dir / "config.yaml").exists()
