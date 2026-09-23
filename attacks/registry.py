from typing import Dict, Any, Optional
from attacks.controller import AttackController

def get_attack_controller(config: Dict[str, Any]) -> AttackController:
    """Factory method to get configured AttackController."""
    return AttackController(config)
