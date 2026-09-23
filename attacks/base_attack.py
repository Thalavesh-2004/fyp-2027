from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAttack(ABC):
    """Abstract base class for all Byzantine attack implementations."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def apply(self, record: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply attack to record or aggregate context.
        
        Returns modified dictionary record or metadata indicating action.
        """
        pass
