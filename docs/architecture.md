# Architecture Specification — September 2026 Milestone

## 1. Overview

The system establishes a distributed, reproducible Apache Spark Structured Streaming research testbed with controlled Byzantine fault injection.

```text
Kafka Event Source (sensor-stream)
             │
             ▼
Spark Structured Streaming App
             │
   ┌─────────┴─────────┐
   ▼                   ▼
Normal Executor   Byzantine Executor (Controlled Fault Injection)
   │                   │
   └─────────┬─────────┘
             ▼
      Streaming Output Sink
             │
             ├────────────────────────────────┐
             ▼                                ▼
Independent Ground Truth Validator    SQLite / Parquet Storage
             │                                │
             └────────────────────────────────┘
                               │
                               ▼
                    Metrics & Research Plots
```

## 2. Infrastructure Topology

- **Container Orchestration**: Docker Compose
- **Spark Cluster**: 1 Master (`spark-master`), 3 Workers (`spark-worker-1`, `spark-worker-2`, `spark-worker-3`)
- **Message Broker**: Apache Kafka + Zookeeper (`kafka:9092`)
- **Execution Runtime**: Python 3.10+, PySpark 3.5.0, Java 17

## 3. Data Flow & Aggregations

1. Synthetic IoT events published to Kafka topic `sensor-stream`.
2. PySpark micro-batch consumer ingests events with explicit `StructType` schema (`event_id`, `timestamp`, `sensor_id`, `temperature`, `humidity`).
3. Deterministic aggregations compute per-sensor averages, counts, min/max values.
4. `AttackController` injects specified fault types (`VALUE_CORRUPTION`, `WRONG_AGGREGATION`, `DROP_COMPUTATION`, `DELAY`) based on configured probability and target worker matching.
5. Results saved per experiment under `output/experiment_results/<experiment_id>/`.
6. Independent Ground Truth engine computes expected aggregates directly from input events and measures error rates.
