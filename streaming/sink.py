import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ResultSink:
    """Handles saving batch streaming metrics and results to files."""

    def __init__(self, output_dir: str, experiment_id: str):
        self.output_dir = Path(output_dir) / experiment_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.output_dir / "raw_results.json"
        self.execution_file = self.output_dir / "execution_records.json"

    def write_batch_results(self, batch_id: int, records: List[Dict[str, Any]]):
        """Append batch result records to raw results storage."""
        existing = []
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        batch_payload = {
            "batch_id": batch_id,
            "record_count": len(records),
            "records": records
        }
        existing.append(batch_payload)

        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)

    def write_execution_records(self, records: List[Dict[str, Any]]):
        """Save execution metadata records."""
        with open(self.execution_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2)
