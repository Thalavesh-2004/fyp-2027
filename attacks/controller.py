import random
import socket
import logging
from typing import Dict, Any, Optional, List
from attacks.base_attack import BaseAttack
from attacks.value_corruption import ValueCorruptionAttack
from attacks.wrong_aggregation import WrongAggregationAttack
from attacks.drop_computation import DropComputationAttack
from attacks.delay_attack import DelayAttack

logger = logging.getLogger(__name__)

class AttackController:
    """Manages attack execution decisions based on configuration, probability, and targets."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("attack", {})
        self.enabled = self.config.get("enabled", False)
        self.attack_type = self.config.get("type", "NONE").upper()
        self.probability = float(self.config.get("probability", 0.0))
        self.target_workers = self.config.get("target_workers", [])
        self.random_seed = self.config.get("random_seed", 42)
        self.rng = random.Random(self.random_seed)
        
        self.attack_instance = self._create_attack_instance()
        self.attempted_count = 0
        self.successful_count = 0

    def _create_attack_instance(self) -> Optional[BaseAttack]:
        if not self.enabled or self.attack_type == "NONE":
            return None

        if self.attack_type == "VALUE_CORRUPTION":
            cfg = self.config.get("corruption", {})
            return ValueCorruptionAttack(
                strategy=cfg.get("strategy", "additive"),
                value=float(cfg.get("value", 50.0)),
                target_field=cfg.get("target_field", "temperature")
            )
        elif self.attack_type == "WRONG_AGGREGATION":
            cfg = self.config.get("wrong_aggregation", {})
            return WrongAggregationAttack(
                strategy=cfg.get("strategy", "offset"),
                offset=float(cfg.get("offset", 25.0))
            )
        elif self.attack_type == "DROP_COMPUTATION":
            cfg = self.config.get("drop", {})
            return DropComputationAttack(
                drop_probability=float(cfg.get("probability", self.probability))
            )
        elif self.attack_type == "DELAY":
            cfg = self.config.get("delay", {})
            return DelayAttack(
                delay_ms=int(cfg.get("milliseconds", 2000))
            )
        return None

    def should_attack(self, current_hostname: Optional[str] = None) -> bool:
        if not self.enabled or self.attack_instance is None:
            return False

        # Target worker matching check
        if current_hostname and self.target_workers:
            if not any(target in current_hostname for target in self.target_workers):
                return False

        # Probability check using deterministic random generator
        return self.rng.random() < self.probability

    def process_record(self, record: Dict[str, Any], hostname: Optional[str] = None) -> Dict[str, Any]:
        """Apply attack to a record if eligible."""
        if not hostname:
            try:
                hostname = socket.gethostname()
            except Exception:
                hostname = "unknown-host"

        is_eligible = self.should_attack(hostname)
        if is_eligible and self.attack_instance:
            self.attempted_count += 1
            result = self.attack_instance.apply(record, {"hostname": hostname})
            if result.get("attack_applied", False):
                self.successful_count += 1
            result["executor_hostname"] = hostname
            return result

        unmodified = record.copy()
        unmodified["attack_applied"] = False
        unmodified["attack_type"] = "NONE"
        unmodified["executor_hostname"] = hostname
        return unmodified
