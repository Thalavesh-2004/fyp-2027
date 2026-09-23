import logging
from typing import Dict, Any, Optional
from attacks.base_attack import BaseAttack

logger = logging.getLogger(__name__)

class DropComputationAttack(BaseAttack):
    """Simulates selective omission of input data or computation tasks."""

    def __init__(self, drop_probability: float = 0.20):
        super().__init__("DROP_COMPUTATION", {"drop_probability": drop_probability})
        self.drop_probability = drop_probability

    def apply(self, record: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        modified = record.copy()
        modified["dropped"] = True
        modified["attack_applied"] = True
        modified["attack_type"] = self.name
        return modified
