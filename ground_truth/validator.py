import logging
from typing import List, Dict, Any
from ground_truth.calculator import GroundTruthCalculator
from ground_truth.comparator import GroundTruthComparator

logger = logging.getLogger(__name__)

class GroundTruthValidator:
    """Validator orchestrating ground-truth evaluation and summary metrics."""

    def __init__(self, tolerance: float = 0.01):
        self.calculator = GroundTruthCalculator()
        self.comparator = GroundTruthComparator(tolerance=tolerance)

    def validate(self, raw_events: List[Dict[str, Any]], actual_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs ground-truth comparison and reports accuracy metrics."""
        expected_summaries = self.calculator.calculate_expected_aggregates(raw_events)
        comparison_records = self.comparator.compare_summaries(actual_summaries, expected_summaries)

        total_sensors = len(comparison_records)
        correct_count = sum(1 for r in comparison_records if r["is_correct"])
        incorrect_count = total_sensors - correct_count
        accuracy_rate = correct_count / total_sensors if total_sensors > 0 else 1.0

        logger.info(f"Ground Truth Validation: total={total_sensors}, correct={correct_count}, incorrect={incorrect_count}, accuracy={accuracy_rate*100:.1f}%")

        return {
            "total_items": total_sensors,
            "correct_items": correct_count,
            "incorrect_items": incorrect_count,
            "accuracy_rate": accuracy_rate,
            "corruption_rate": 1.0 - accuracy_rate,
            "details": comparison_records
        }
