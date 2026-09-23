import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_experiment_checkpoint_dir(base_dir: str, experiment_id: str) -> str:
    """Create and return clean checkpoint path for experiment."""
    checkpoint_path = Path(base_dir) / experiment_id
    checkpoint_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Checkpoint directory set to: {checkpoint_path}")
    return str(checkpoint_path)

def clean_checkpoint_dir(checkpoint_dir: str):
    """Clean checkpoint directory before a fresh experiment run."""
    path = Path(checkpoint_dir)
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cleaned checkpoint directory: {checkpoint_dir}")
