import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ExperimentDatabase:
    """Manages SQLite persistence for experiment metadata and metrics."""

    def __init__(self, db_path: str = "output/experiments.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def init_db(self):
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
            logger.info(f"Database initialized at {self.db_path}")

    def insert_experiment(self, exp_meta: Dict[str, Any]):
        sql = """
        INSERT OR REPLACE INTO experiments (
            experiment_id, name, started_at, completed_at, random_seed,
            spark_version, python_version, worker_count, input_record_count,
            input_rate, attack_enabled, attack_type, attack_probability, configuration_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            exp_meta.get("experiment_id"), exp_meta.get("name"),
            exp_meta.get("started_at"), exp_meta.get("completed_at"),
            exp_meta.get("random_seed"), exp_meta.get("spark_version"),
            exp_meta.get("python_version"), exp_meta.get("worker_count"),
            exp_meta.get("input_record_count"), exp_meta.get("input_rate"),
            1 if exp_meta.get("attack_enabled") else 0,
            exp_meta.get("attack_type"), exp_meta.get("attack_probability"),
            exp_meta.get("configuration_path")
        )
        with self.get_connection() as conn:
            conn.execute(sql, params)

    def insert_summary(self, summary: Dict[str, Any]):
        sql = """
        INSERT OR REPLACE INTO experiment_summary (
            experiment_id, total_input_records, total_output_records,
            correct_results, incorrect_results, attack_attempts, successful_attacks,
            corruption_rate, throughput_records_per_second, average_latency_ms,
            p95_latency_ms, total_processing_time_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            summary.get("experiment_id"), summary.get("total_input_records"),
            summary.get("total_output_records"), summary.get("correct_results"),
            summary.get("incorrect_results"), summary.get("attack_attempts"),
            summary.get("successful_attacks"), summary.get("corruption_rate"),
            summary.get("throughput_records_per_second"), summary.get("average_latency_ms"),
            summary.get("p95_latency_ms"), summary.get("total_processing_time_ms")
        )
        with self.get_connection() as conn:
            conn.execute(sql, params)

    def insert_execution_records(self, records: List[Dict[str, Any]]):
        sql = """
        INSERT INTO execution_records (
            experiment_id, batch_id, stage_id, task_id, partition_id,
            executor_id, hostname, duration_ms, input_count, output_count,
            attack_applied, attack_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params_list = [
            (
                r.get("experiment_id"), r.get("batch_id"), r.get("stage_id"),
                r.get("task_id"), r.get("partition_id"), r.get("executor_id"),
                r.get("hostname"), r.get("duration_ms"), r.get("input_count"),
                r.get("output_count"), 1 if r.get("attack_applied") else 0,
                r.get("attack_type")
            ) for r in records
        ]
        with self.get_connection() as conn:
            conn.executemany(sql, params_list)
