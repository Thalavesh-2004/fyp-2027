# Apache Spark Structured Streaming Byzantine Fault Testbed

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Spark 3.5.0](https://img.shields.io/badge/spark-3.5.0-orange.svg)](https://spark.apache.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **September 2026 Milestone**: Baseline Apache Spark Structured Streaming Implementation + Byzantine Attack Simulation.

## 📌 Overview

This project establishes a reproducible, distributed streaming research environment designed to simulate and quantify the impact of Byzantine worker behavior on Apache Spark Structured Streaming applications.

### Key Capabilities
- **Dockerized Multi-Worker Cluster**: 3 Spark workers (`spark-worker-1`, `spark-worker-2`, `spark-worker-3`) with Master UI on port 8080.
- **Kafka Streaming Ingestion**: Continuous ingestion of synthetic IoT sensor events.
- **Controlled Byzantine Fault Injection**: Configurable attack controller supporting:
  - `VALUE_CORRUPTION` (additive, multiplicative, replacement)
  - `WRONG_AGGREGATION` (offset, multiplier, fixed replacement)
  - `DROP_COMPUTATION` (omitting records/tasks)
  - `DELAY` (latency injection)
- **Independent Ground Truth Validation**: Dual computation path comparing Spark outputs against trusted reference calculations.
- **Automated Experiment Life-Cycle**: CLI runner (`run_experiment.py`) with SQLite persistence and Matplotlib graph generation.

---

## 🚀 Quick Start

### 1. Requirements
- Docker & Docker Compose
- Python 3.10+

### 2. Setup & Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Docker cluster (Kafka + Spark Master + 3 Workers)
make up
```

### 3. Run Experiments
```bash
# Run Baseline Experiment (0% attack)
python experiments/run_experiment.py --config config/baseline.yaml

# Run Value Corruption Attack Experiment (20% attack)
python experiments/run_experiment.py --config config/value_corruption_20.yaml

# Analyze all runs and generate research plots
python analysis/analyze_results.py

# Generate interactive web dashboard
python dashboard/generate_dashboard.py
```

### 4. Run Automated Tests
```bash
pytest tests/ -v
```

---

## 📁 Repository Structure
```text
spark-byzantine-streaming/
├── docker-compose.yml
├── requirements.txt
├── Makefile
├── config/                  # Experiment YAML configurations
├── producer/                # Synthetic IoT Kafka producer
├── streaming/               # PySpark Structured Streaming application
├── attacks/                 # Byzantine attack simulation framework
├── execution/               # Worker identity & task context tracking
├── ground_truth/            # Independent trusted validator
├── database/                # SQLite metadata & results schema
├── experiments/             # Experiment lifecycle runner & metrics
├── analysis/                # Research visualization & plot generation
├── tests/                   # Unit and integration test suites
└── docs/                    # Architecture & threat model documentation
```

---

## 📝 License
Distributed under the MIT License.
