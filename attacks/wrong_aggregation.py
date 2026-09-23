import logging
from typing import Dict, Any, Optional
from attacks.base_attack import BaseAttack

logger = logging.getLogger(__name__)

class WrongAggregationAttack(BaseAttack):
    """Produces mathematically incorrect window/batch aggregate results."""

    def __init__(self, strategy: str = "offset", offset: float = 25.0, multiplier: float = 1.5, fixed_value: float = 999.0):
        super().__init__("WRONG_AGGREGATION", {"strategy": strategy, "offset": offset, "multiplier": multiplier, "fixed_value": fixed_value})
        self.strategy = strategy
        self.offset = offset
        self.multiplier = multiplier
        self.fixed_value = fixed_value

    def apply(self, record: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        modified = record.copy()
        target_field = "avg_temperature" if "avg_temperature" in modified else "temperature"
        
        if target_field not in modified or modified[target_field] is None:
            return modified

        orig_val = float(modified[target_field])
        if self.strategy == "offset":
            new_val = orig_val + self.offset
        elif self.strategy == "multiplier":
            new_val = orig_val * self.multiplier
        elif self.strategy == "fixed":
            new_val = self.fixed_value
        else:
            new_val = orig_val + self.offset

        modified[target_field] = round(new_val, 2)
        modified["attack_applied"] = True
        modified["attack_type"] = self.name
        modified["original_value"] = str(orig_val)
        modified["modified_value"] = str(modified[target_field])
        return modified
