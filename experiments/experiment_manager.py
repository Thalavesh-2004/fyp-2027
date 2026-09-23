import os
import sys
import yaml
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from producer.sensor_producer import SensorProducer
from streaming.streaming_app import SparkByzantineStreamingApp
from ground_truth.validator import GroundTruthValidator
from experiments.metrics import ExperimentMetricsCalculator
from database.database import ExperimentDatabase
from execution.execution_logger import setup_logger
from analysis.plots import ExperimentPlotter

class ExperimentManager:
    """Orchestrates complete experiment execution, ground truth validation, metrics logging, and database storage."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        
        self.exp_cfg = self.config.get("experiment", {})
        self.experiment_id = self.exp_cfg.get("id", f"exp_{int(datetime.now().timestamp())}")
        self.output_dir = Path("output/experiment_results") / self.experiment_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.output_dir / "experiment.log"
        self.logger = setup_logger(f"exp_{self.experiment_id}", str(self.log_file))
        self.db = ExperimentDatabase()

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def run(self) -> Dict[str, Any]:
        self.logger.info(f"=== Starting Experiment: {self.exp_cfg.get('name', self.experiment_id)} ===")
        started_at = datetime.now(timezone.utc).isoformat()

        # Save config copy into output directory
        with open(self.output_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f)

        # 1. Event Producer
        prod_cfg = self.config.get("producer", {})
        producer = SensorProducer(
            bootstrap_servers=self.config.get("stream", {}).get("bootstrap_servers", "localhost:29092"),
            topic=self.config.get("stream", {}).get("kafka_topic", "sensor-stream"),
            events_per_second=prod_cfg.get("events_per_second", 500),
            total_events=prod_cfg.get("total_events", 10000),
            random_seed=prod_cfg.get("random_seed", 42)
        )
        raw_events = producer.publish_all(mock=True)

        # 2. Spark Streaming Execution
        streaming_app = SparkByzantineStreamingApp(self.config)
        streaming_results = streaming_app.run_batch_simulation(raw_events, batch_size=2000)

        # 3. Ground Truth Validation
        validator = GroundTruthValidator(tolerance=0.01)
        validation_results = validator.validate(raw_events, streaming_results["all_summaries"])

        # 4. Metrics Calculation
        metrics = ExperimentMetricsCalculator.compute_metrics(
            experiment_id=self.experiment_id,
            streaming_result=streaming_results,
            validation_result=validation_results
        )
        completed_at = datetime.now(timezone.utc).isoformat()

        # 5. Persist Results & SQLite DB
        summary_payload = {
            **metrics,
            "experiment_name": self.exp_cfg.get("name"),
            "attack_type": self.config.get("attack", {}).get("type", "NONE"),
            "attack_probability": self.config.get("attack", {}).get("probability", 0.0),
            "input_rate": prod_cfg.get("events_per_second", 500)
        }

        with open(self.output_dir / "metrics.json", 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)

        with open(self.output_dir / "summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary_payload, f, indent=2)

        # Database Insertion
        exp_meta = {
            "experiment_id": self.experiment_id,
            "name": self.exp_cfg.get("name"),
            "started_at": started_at,
            "completed_at": completed_at,
            "random_seed": prod_cfg.get("random_seed", 42),
            "spark_version": "3.5.0",
            "python_version": sys.version.split()[0],
            "worker_count": self.exp_cfg.get("worker_count", 3),
            "input_record_count": metrics["total_input_records"],
            "input_rate": prod_cfg.get("events_per_second", 500),
            "attack_enabled": self.config.get("attack", {}).get("enabled", False),
            "attack_type": self.config.get("attack", {}).get("type", "NONE"),
            "attack_probability": self.config.get("attack", {}).get("probability", 0.0),
            "configuration_path": self.config_path
        }
        self.db.insert_experiment(exp_meta)
        self.db.insert_summary(metrics)
        self.db.insert_execution_records(streaming_results["execution_records"])

        # 6. Generate plot for single experiment
        plotter = ExperimentPlotter(str(self.output_dir / "plots"))
        plotter.generate_all_plots([summary_payload])

        self.logger.info(f"=== Completed Experiment {self.experiment_id} successfully ===")
        return summary_payload
