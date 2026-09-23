import logging
from typing import Dict, Any, Optional
from attacks.base_attack import BaseAttack

logger = logging.getLogger(__name__)

class ValueCorruptionAttack(BaseAttack):
    """Corrupts numerical sensor values (e.g. temperature, humidity)."""

    def __init__(self, strategy: str = "additive", value: float = 50.0, target_field: str = "temperature"):
        super().__init__("VALUE_CORRUPTION", {"strategy": strategy, "value": value, "target_field": target_field})
        self.strategy = strategy
        self.value = value
        self.target_field = target_field

    def apply(self, record: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        modified = record.copy()
        if self.target_field not in modified or modified[self.target_field] is None:
            return modified

        orig_val = float(modified[self.target_field])
        if self.strategy == "additive":
            new_val = orig_val + self.value
        elif self.strategy == "multiplicative":
            new_val = orig_val * self.value
        elif self.strategy == "replacement":
            new_val = self.value
        else:
            new_val = orig_val + self.value

        modified[self.target_field] = round(new_val, 2)
        modified["attack_applied"] = True
        modified["attack_type"] = self.name
        modified["original_value"] = str(orig_val)
        modified["modified_value"] = str(modified[self.target_field])
        return modified
