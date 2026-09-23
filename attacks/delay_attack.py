import time
import logging
from typing import Dict, Any, Optional
from attacks.base_attack import BaseAttack

logger = logging.getLogger(__name__)

class DelayAttack(BaseAttack):
    """Deliberately delays task execution to induce latency."""

    def __init__(self, delay_ms: int = 500):
        super().__init__("DELAY", {"delay_ms": delay_ms})
        self.delay_ms = delay_ms
        self.delayed_batches = set()

    def apply(self, record: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        modified = record.copy()
        batch_id = context.get("batch_id", 1) if context else 1
        
        # Delay once per batch task context
        if batch_id not in self.delayed_batches:
            if self.delay_ms > 0:
                time.sleep(self.delay_ms / 1000.0)
            self.delayed_batches.add(batch_id)

        modified["attack_applied"] = True
        modified["attack_type"] = self.name
        modified["delay_ms"] = self.delay_ms
        return modified
