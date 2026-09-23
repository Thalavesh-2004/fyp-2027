from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class TaskMetadata:
    experiment_id: str
    batch_id: int
    stage_id: Optional[int] = None
    task_id: Optional[int] = None
    partition_id: Optional[int] = None
    executor_id: Optional[str] = None
    hostname: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    input_count: int = 0
    output_count: int = 0
    attack_applied: bool = False
    attack_type: str = "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
