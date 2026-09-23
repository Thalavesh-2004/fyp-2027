import socket
import os
from typing import Dict, Any, Optional

def get_execution_identity() -> Dict[str, Any]:
    """Capture current Spark TaskContext or local environment metadata."""
    identity = {
        "hostname": socket.gethostname(),
        "executor_id": os.environ.get("SPARK_EXECUTOR_ID", "driver"),
        "stage_id": None,
        "partition_id": None,
        "task_id": None,
        "task_attempt": None
    }

    try:
        from pyspark import TaskContext
        context = TaskContext.get()
        if context is not None:
            identity["stage_id"] = context.stageId()
            identity["partition_id"] = context.partitionId()
            identity["task_id"] = context.taskId()
            identity["task_attempt"] = context.attemptNumber()
            # In Spark, executorId can be fetched from TaskContext resources or environment
    except Exception:
        pass

    return identity
