import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class JSONFormatter(logging.Formatter):
    """Formats log records as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        return json.dumps(log_data)

def setup_logger(name: str = "spark_byzantine", log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configures structured JSON logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    # Console handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(level)
    c_handler.setFormatter(JSONFormatter())
    logger.addHandler(c_handler)

    # File handler if specified
    if log_file:
        f_handler = logging.FileHandler(log_file, encoding='utf-8')
        f_handler.setLevel(level)
        f_handler.setFormatter(JSONFormatter())
        logger.addHandler(f_handler)

    return logger

def log_execution_event(logger: logging.Logger, event_name: str, details: Dict[str, Any]):
    """Log structured execution or attack event."""
    extra = {"extra_fields": {"event_name": event_name, **details}}
    logger.info(f"Execution Event: {event_name}", extra=extra)
