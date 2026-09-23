#!/bin/bash
CONFIG=${1:-config/value_corruption_20.yaml}
echo "Running Byzantine Attack Experiment using config: $CONFIG"
python experiments/run_experiment.py --config "$CONFIG"
