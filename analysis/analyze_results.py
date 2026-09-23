import sqlite3
import json
import logging
from pathlib import Path
from database.database import ExperimentDatabase
from analysis.plots import ExperimentPlotter

logger = logging.getLogger(__name__)

def analyze_all_experiments(db_path: str = "output/experiments.db", output_dir: str = "output/figures"):
    """Reads all experiment summaries from SQLite DB and generates visualization charts."""
    db = ExperimentDatabase(db_path)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.experiment_id, e.name, e.attack_enabled, e.attack_type, e.attack_probability,
                   e.input_rate, s.total_input_records, s.total_output_records, s.correct_results,
                   s.incorrect_results, s.corruption_rate, s.throughput_records_per_second,
                   s.average_latency_ms, s.p95_latency_ms
            FROM experiment_summary s
            JOIN experiments e ON s.experiment_id = e.experiment_id
            ORDER BY e.attack_probability ASC
        """)
        rows = cursor.fetchall()

    summaries = []
    for r in rows:
        summaries.append({
            "experiment_id": r[0],
            "name": r[1],
            "attack_enabled": bool(r[2]),
            "attack_type": r[3],
            "attack_probability": r[4],
            "input_rate": r[5],
            "total_input_records": r[6],
            "total_output_records": r[7],
            "correct_results": r[8],
            "incorrect_results": r[9],
            "corruption_rate": r[10],
            "throughput_records_per_second": r[11],
            "average_latency_ms": r[12],
            "p95_latency_ms": r[13]
        })

    logger.info(f"Loaded {len(summaries)} experiment summaries for analysis.")
    plotter = ExperimentPlotter(output_dir)
    plotter.generate_all_plots(summaries)
    logger.info(f"Generated research plots in {output_dir}")

if __name__ == "__main__":
    analyze_all_experiments()
