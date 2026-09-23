# 1. Executive Summary & Goal

## Project Title

**Fault Tolerance in Apache Spark Structured Streaming using Trust-Aware Adaptive Scheduling under Byzantine Nodes**

## Current Implementation Phase

This implementation is **Phase 1 of a larger one-year research project**.

The current phase corresponds to the September milestone in the project plan:

> **Baseline Spark Structured Streaming Implementation + Byzantine Attack Simulation**

Do **not** implement the trust-management module, adaptive verification module, or trust-aware scheduler yet. The September implementation must establish a clean, reproducible experimental foundation for those later components.

The eventual research pipeline is:

```text
Kafka Streaming Data
        │
        ▼
Spark Structured Streaming
        │
        ▼
Distributed Task Execution
        │
        ├───────────────┐
        ▼               ▼
 Normal Executor   Byzantine Executor
        │               │
        │               └── Incorrect / modified / delayed result
        │
        └───────────────┐
                        ▼
              Adaptive Verification
                        │
                        ▼
                 Trust Management
                        │
                        ▼
             Trust-Aware Scheduler
                        │
                        ▼
              Adaptive Replication
```

The current implementation must stop after establishing the following:

```text
Kafka
  ↓
Spark Structured Streaming
  ↓
Multi-worker Spark cluster
  ↓
Controlled Byzantine fault injection
  ↓
Ground-truth comparison
  ↓
Experimental metrics
```

## Primary Goal

Build a working distributed streaming testbed that demonstrates experimentally that:

1. Spark Structured Streaming can process a continuous event stream.
2. Spark can distribute processing across multiple workers.
3. Normal workers produce correct results.
4. A controlled Byzantine worker can remain operational while deliberately producing incorrect, omitted, or delayed results.
5. The resulting incorrect computation can reach the streaming output without being automatically identified as a Byzantine computation by ordinary Spark task-success semantics.
6. The system can quantify the impact of Byzantine behavior on correctness, latency, and throughput.
7. The generated evidence will become the input for the next project phase: **adaptive verification**.

Spark Structured Streaming commonly processes streams using micro-batches, and its fault-tolerance mechanisms are primarily designed around recovering processing state/input progress rather than independently validating the semantic correctness of a successfully returned computation. The project should therefore explicitly distinguish **failure recovery** from **computation-integrity verification**.

## Research Question for This Phase

> **Can Byzantine behavior in a Spark Structured Streaming environment corrupt streaming computations while the affected executor remains operational, and can this behavior be experimentally characterized in terms of correctness, throughput, and latency?**

## Current Scope

### Must implement

* Kafka-based streaming source.
* Spark Structured Streaming application.
* Spark Standalone multi-worker cluster.
* At least three worker/executor processes.
* Deterministic streaming computation.
* Ground-truth calculation/validation.
* Configurable Byzantine fault injection.
* At least four attack modes:

  * value corruption,
  * incorrect aggregation,
  * computation/data dropping,
  * intentional delay.
* Configurable attack probability/intensity.
* Target-worker configuration.
* Experiment configuration files.
* Structured logging.
* Baseline metrics.
* Attack metrics.
* Reproducible experiments.
* Documentation.
* Docker Compose deployment.

### Must NOT implement in this phase

* Trust scores.
* ML-based malicious-node detection.
* Adaptive verification.
* Merkle trees.
* Blockchain.
* Hyperledger Fabric.
* PBFT.
* Kubernetes.
* Reinforcement-learning scheduler.
* Production-grade Spark scheduler replacement.
* Full Byzantine consensus.

These are outside the September milestone.

## Important Architectural Principle

Do not modify Apache Spark's core scheduler during this phase.

The project eventually intends to introduce trust-aware scheduling, but first the baseline and threat model must be experimentally established.

The Byzantine mechanism should therefore be implemented as a **controlled fault-injection layer inside the worker-side computation path**, with clear documentation that this is a research simulation rather than a claim that the Spark scheduler has been replaced.

## Expected September Demonstration

The coding agent must make it possible to demonstrate:

```text
Experiment A:

10,000 events
0 Byzantine behavior

→ Correct processing
→ Baseline latency
→ Baseline throughput
```

and:

```text
Experiment B:

10,000 events
1 Byzantine worker
20% corruption probability

→ Incorrect results introduced
→ Spark continues processing
→ Corrupted results can reach output
→ Impact is measurable
```

The project must preserve enough information to establish the ground truth independently.

---

# 2. Tech Stack (Languages, Frameworks, Libraries)

## 2.1 Core Technologies

| Technology     | Version Strategy                               | Purpose                                            | Required    |
| -------------- | ---------------------------------------------- | -------------------------------------------------- | ----------- |
| Python         | 3.10+                                          | Application, producer, attack simulation, analysis | Yes         |
| Apache Spark   | Pin a tested 3.5.x or compatible version       | Distributed stream processing                      | Yes         |
| PySpark        | Same Spark version                             | Spark application                                  | Yes         |
| Apache Kafka   | Pin a compatible version                       | Streaming source                                   | Yes         |
| Docker         | Current stable version                         | Reproducible cluster                               | Yes         |
| Docker Compose | Current compatible version                     | Multi-container orchestration                      | Yes         |
| Java           | Version compatible with selected Spark release | Spark runtime                                      | Yes         |
| SQLite         | Built-in                                       | Experiment metadata/results                        | Recommended |
| Pandas         | Current compatible version                     | Result analysis                                    | Yes         |
| Matplotlib     | Current compatible version                     | Graph generation                                   | Yes         |

Do not use unpinned `latest` images in the final repository. Select explicit versions known to work together.

## 2.2 Python Libraries

Use:

```text
pyspark
kafka-python
pandas
numpy
matplotlib
pyyaml
pytest
```

Optional:

```text
psutil
```

for system/resource measurements.

Use the standard library for:

```text
json
csv
hashlib
random
time
datetime
logging
os
socket
uuid
statistics
dataclasses
pathlib
```

Do not add unnecessary libraries.

## 2.3 Spark

Use:

**Apache Spark Structured Streaming**

The application should use:

```python
spark.readStream
```

with Kafka as the source.

Use deterministic transformations such as:

* parsing JSON,
* filtering,
* grouping,
* count,
* average,
* min/max,
* anomaly calculation.

Avoid complicated stateful algorithms in the first implementation.

## 2.4 Kafka

Kafka should provide:

```text
sensor-stream
```

The producer continuously publishes JSON events.

Example:

```json
{
  "event_id": 10001,
  "timestamp": "2026-09-23T10:00:01.000Z",
  "sensor_id": "S001",
  "temperature": 31.4,
  "humidity": 64.2
}
```

## 2.5 Docker

Create containers for:

```text
Kafka
Spark Master
Spark Worker 1
Spark Worker 2
Spark Worker 3
Application/Driver
```

Do not require Kubernetes.

## 2.6 Ground Truth

The system must have an independent trusted computation path.

The ground-truth implementation must not depend on the potentially Byzantine result.

For deterministic transformations, calculate expected results independently from the original event data.

## 2.7 Configuration

Use YAML or JSON configuration.

Example:

```yaml
stream:
  kafka_topic: sensor-stream
  bootstrap_servers: kafka:9092

experiment:
  name: baseline_value_corruption
  duration_seconds: 120
  records: 10000
  random_seed: 42

attack:
  enabled: true
  type: value_corruption
  probability: 0.20
  target_workers:
    - spark-worker-3
  corruption_magnitude: 50.0
```

The attack configuration must be changeable without modifying application source code.

---

# 3. Core Features & Requirements (acceptance criteria per feature)

## Feature 1 — Kafka Streaming Producer

### Purpose

Generate a reproducible continuous stream of synthetic IoT-style events.

### Event schema

Each event must contain:

```text
event_id
timestamp
sensor_id
temperature
humidity
```

### Requirements

* Generate configurable number of events.
* Support configurable events/second.
* Support deterministic random seed.
* Support multiple sensor IDs.
* Publish JSON.
* Publish to configurable Kafka topic.
* Log number of produced events.
* Support graceful shutdown.

### Acceptance Criteria

* Kafka topic can be created automatically or documented.
* Producer successfully sends at least 10,000 events.
* Spark can consume the events.
* Event IDs are unique.
* Producer can reproduce the same sequence using the same seed.

---

# Feature 2 — Spark Structured Streaming Baseline

## Purpose

Create the normal, non-Byzantine reference system.

### Data flow

```text
Kafka
  ↓
Spark Kafka Source
  ↓
JSON Parsing
  ↓
Schema Validation
  ↓
Transformation
  ↓
Aggregation
  ↓
Output Sink
```

### Recommended computation

Calculate per micro-batch or window:

```text
event_count
average_temperature
minimum_temperature
maximum_temperature
average_humidity
```

For example:

```text
window_start
window_end
sensor_id
event_count
avg_temperature
min_temperature
max_temperature
```

### Requirements

* Use Spark Structured Streaming.
* Use explicit schema.
* Use Kafka source.
* Use checkpoint directory.
* Use configurable trigger interval.
* Use configurable output mode.
* Persist results in a machine-readable format.
* Record batch IDs.
* Record processing timestamps.
* Record executor/host information where technically available.
* Fail clearly on malformed input rather than silently producing invalid data.

### Acceptance Criteria

* Stream starts successfully.
* At least 10,000 records can be processed.
* Output is produced continuously.
* No attack enabled means zero deliberately corrupted outputs.
* Checkpoint directory is created.
* Application can restart without losing already committed progress beyond the expected semantics of the chosen sink/source configuration.
* Baseline throughput and latency are recorded.

---

# Feature 3 — Multi-Worker Spark Cluster

## Purpose

Create a distributed environment in which different executor processes can be observed.

### Minimum topology

```text
Spark Master
     │
     ├── Worker 1
     ├── Worker 2
     └── Worker 3
```

### Requirements

* Three Spark workers minimum.
* Workers must have identifiable names.
* Spark UI must be accessible.
* Worker resource configuration must be explicit.
* Worker logs must be accessible.
* Container names must be stable.

### Acceptance Criteria

Spark UI must show:

```text
Worker 1
Worker 2
Worker 3
```

and the application must execute distributed tasks.

---

# Feature 4 — Worker Identification

## Purpose

Every computation must be traceable to the worker/executor that processed it whenever the Spark execution context exposes that information.

Capture:

```text
executor_id
hostname
partition_id
task_id
stage_id
batch_id
timestamp
```

Do not assume that application-level code can deterministically choose the Spark worker for every task.

The implementation must record the actual execution identity where available.

### Acceptance Criteria

Every experimental result should contain enough metadata to identify:

```text
batch
partition
task
executor/host
```

where available.

---

# Feature 5 — Byzantine Attack Controller

## Purpose

Provide a centralized, configurable mechanism for enabling/disabling attacks.

Example:

```yaml
attack:
  enabled: true
  type: value_corruption
  probability: 0.20
```

### Supported attack types

```text
NONE
VALUE_CORRUPTION
WRONG_AGGREGATION
DROP_COMPUTATION
DELAY
```

### Acceptance Criteria

* Attack can be enabled/disabled without code modification.
* Attack type can be changed through configuration.
* Attack probability can be changed.
* Target worker can be configured.
* Attack behavior is logged.
* Normal mode must produce no attack modifications.

---

# Feature 6 — Value Corruption Attack

## Purpose

Modify otherwise valid computed values.

Example:

```text
Correct temperature:

31.4

Corrupted:

81.4
```

### Requirements

Support configurable corruption strategies:

```text
additive
multiplicative
replacement
```

Example:

```yaml
corruption:
  strategy: additive
  value: 50
```

### Acceptance Criteria

With attack probability `1.0`, every eligible computation handled by a targeted Byzantine process must be modified.

With probability `0.0`, no modification occurs.

---

# Feature 7 — Wrong Aggregation Attack

## Purpose

Return a mathematically incorrect aggregation.

Example:

```text
Correct average:

31.5

Byzantine result:

51.5
```

Support:

```text
offset
multiplication
fixed replacement
```

### Acceptance Criteria

The attack produces intentionally incorrect results while the process itself remains operational.

---

# Feature 8 — Computation/Data Drop Attack

## Purpose

Simulate a worker selectively omitting data or computation.

Example:

```text
Expected:
100 events

Returned:
70 events
```

### Requirements

Configurable:

```yaml
drop:
  probability: 0.30
```

The implementation must distinguish:

```text
input records
processed records
dropped records
```

### Acceptance Criteria

The experiment can quantify how many records were intentionally omitted.

---

# Feature 9 — Delay Attack

## Purpose

Simulate a Byzantine/straggling worker deliberately delaying computation.

Configuration:

```yaml
delay:
  enabled: true
  milliseconds: 5000
```

### Requirements

* Configurable delay.
* Configurable probability.
* Log delay events.
* Do not automatically label every slow execution as Byzantine.
* Treat this attack as a timing-behavior experiment.

### Acceptance Criteria

The experiment demonstrates increased processing latency or task delay under controlled conditions.

---

# Feature 10 — Attack Probability

Every attack except `NONE` should support:

```text
0.0
0.05
0.10
0.20
0.30
0.50
1.0
```

Interpretation:

```text
0.10 = approximately 10% of eligible operations are attacked
```

Use a configurable deterministic random seed for reproducibility.

### Acceptance Criteria

Repeated runs with the same configuration and seed produce statistically similar attack counts.

---

# Feature 11 — Target Worker Configuration

The system should support:

```yaml
target_workers:
  - spark-worker-3
```

However, do not assume Spark guarantees that a particular task will execute on that worker.

The implementation should:

1. identify the current execution environment;
2. determine whether it matches a configured target;
3. inject the attack only when the execution environment is eligible;
4. log the actual executor/hostname.

If exact executor placement cannot be guaranteed through the chosen architecture, document this limitation rather than falsely claiming deterministic worker placement.

### Acceptance Criteria

The logs clearly show:

```text
actual executor/host
target configuration
whether attack was applied
```

---

# Feature 12 — Ground-Truth Validator

## Purpose

Determine whether a result is actually correct.

This is essential.

The system must not infer correctness merely because Spark reports task success.

### Architecture

```text
Original Events
      │
      ├──────────► Spark computation
      │                    │
      │                    ▼
      │              Spark output
      │
      └──────────► Independent ground truth
                           │
                           ▼
                     Expected output
```

### Requirements

* Maintain trusted input/reference data.
* Independently calculate expected aggregates.
* Compare expected and actual results.
* Support exact comparison for integer/count values.
* Support configurable numerical tolerance for floating-point values.

### Acceptance Criteria

The validator reports:

```text
expected_value
actual_value
absolute_error
relative_error
correct/incorrect
```

Example:

```json
{
  "expected_avg": 31.42,
  "actual_avg": 81.42,
  "absolute_error": 50.0,
  "correct": false
}
```

---

# Feature 13 — Experimental Metrics

Collect at minimum:

### Correctness

```text
total_results
correct_results
incorrect_results
corruption_rate
```

### Throughput

```text
input_records_per_second
processed_records_per_second
```

### Latency

```text
event_to_output_latency
batch_processing_time
```

### Attack metrics

```text
attack_attempts
successful_corruptions
dropped_records
delayed_tasks
```

### Resource metrics

Where practical:

```text
CPU
memory
```

### Acceptance Criteria

Every experiment produces machine-readable metrics.

---

# Feature 14 — Experiment Runner

Create a single command such as:

```bash
python experiments/run_experiment.py --config configs/baseline.yaml
```

The runner should:

1. validate configuration;
2. start/verify Kafka;
3. verify Spark;
4. clear or create experiment output directories safely;
5. start the producer;
6. start the Spark streaming application;
7. wait for configured duration/record count;
8. stop cleanly;
9. run ground-truth validation;
10. calculate metrics;
11. save results;
12. generate plots.

---

# Feature 15 — Experiment Configurations

Create predefined configurations:

```text
baseline.yaml
value_corruption_5.yaml
value_corruption_10.yaml
value_corruption_20.yaml
value_corruption_50.yaml
wrong_aggregation.yaml
drop_attack.yaml
delay_attack.yaml
```

This allows systematic experimentation.

---

# Feature 16 — Visualization

Generate:

1. Attack rate vs incorrect-result rate.
2. Attack rate vs throughput.
3. Attack rate vs latency.
4. Attack type vs incorrect results.
5. Attack type vs latency.
6. Input rate vs processing throughput.
7. Batch processing time over time.

Do not fabricate results. Graphs must be generated from actual experiment data.

---

# Feature 17 — Logging

Use structured logs.

Every relevant operation should include:

```text
timestamp
experiment_id
batch_id
partition_id
task_id
executor_id
hostname
attack_type
attack_enabled
attack_applied
attack_probability
```

Use Python `logging`.

Avoid scattered `print()` statements in production code.

---

# Feature 18 — Reproducibility

Every experiment must record:

```text
experiment_id
configuration
random_seed
Spark version
Python version
Kafka version
Docker image/version
timestamp
number_of_workers
input_rate
attack_type
attack_probability
```

Store configuration alongside results.

---

# Feature 19 — Baseline Experiment

Configuration:

```yaml
attack:
  enabled: false
```

Run:

```text
10,000 records
3 workers
no attack
```

Expected:

```text
0 deliberate corruptions
```

Record:

* throughput,
* latency,
* output correctness,
* CPU,
* memory.

---

# Feature 20 — Byzantine Experiments

Run:

```text
5%
10%
20%
30%
50%
```

for each suitable attack.

The first priority is:

```text
Value corruption
```

Then:

```text
Wrong aggregation
Drop
Delay
```

---

# Feature 21 — Spark Checkpointing

Configure a checkpoint directory for the streaming query.

Example conceptual location:

```text
/checkpoints/baseline
```

Do not treat checkpointing as a Byzantine defense.

Document the distinction:

```text
Checkpointing:
recovers stream-processing state/progress.

Byzantine verification:
checks whether computation results are correct.
```

The project should experimentally demonstrate this conceptual difference.

---

# Feature 22 — Security and Safety

The attack simulator must remain controlled.

It must:

* operate only inside the local Docker/project environment;
* not attack external systems;
* not modify host operating-system files;
* not perform network attacks;
* not generate uncontrolled traffic;
* provide explicit attack enable/disable configuration.

---

# Feature 23 — Future-Compatibility Hooks

The September implementation must be designed so later modules can consume its output.

Create interfaces such as:

```text
VerificationRecord
WorkerBehaviorRecord
ExperimentResult
ExecutorObservation
```

Future modules will consume:

```text
ExecutorObservation
        ↓
Trust Manager
        ↓
Trust Score
        ↓
Scheduler
```

Do not implement the trust algorithm now.

---

# 4. Database Schema / Data Models

## Database Strategy

The streaming pipeline itself does not require a relational database.

Use:

* Kafka for event streaming.
* Parquet/JSON/CSV for raw experiment output.
* SQLite for experiment metadata and summarized results.

This keeps the system lightweight.

---

## 4.1 Event Model

```text
Event
```

Fields:

| Field       | Type      | Description         |
| ----------- | --------- | ------------------- |
| event_id    | INTEGER   | Unique event ID     |
| timestamp   | TIMESTAMP | Event creation time |
| sensor_id   | STRING    | Sensor identifier   |
| temperature | FLOAT     | Temperature         |
| humidity    | FLOAT     | Humidity            |

Example:

```json
{
  "event_id": 1001,
  "timestamp": "2026-09-23T10:00:01Z",
  "sensor_id": "S001",
  "temperature": 31.4,
  "humidity": 64.2
}
```

---

# 4.2 Experiment Table

```sql
CREATE TABLE experiments (
    experiment_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    random_seed INTEGER,
    spark_version TEXT,
    python_version TEXT,
    worker_count INTEGER,
    input_record_count INTEGER,
    input_rate REAL,
    attack_enabled INTEGER,
    attack_type TEXT,
    attack_probability REAL,
    configuration_path TEXT
);
```

---

# 4.3 Execution Record

```sql
CREATE TABLE execution_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT,
    batch_id INTEGER,
    stage_id INTEGER,
    task_id INTEGER,
    partition_id INTEGER,
    executor_id TEXT,
    hostname TEXT,
    started_at TEXT,
    completed_at TEXT,
    duration_ms REAL,
    input_count INTEGER,
    output_count INTEGER,
    attack_applied INTEGER,
    attack_type TEXT
);
```

---

# 4.4 Validation Results

```sql
CREATE TABLE validation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT,
    batch_id INTEGER,
    partition_id INTEGER,
    metric_name TEXT,
    expected_value REAL,
    actual_value REAL,
    absolute_error REAL,
    relative_error REAL,
    is_correct INTEGER
);
```

---

# 4.5 Attack Events

```sql
CREATE TABLE attack_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT,
    timestamp TEXT,
    executor_id TEXT,
    hostname TEXT,
    attack_type TEXT,
    probability REAL,
    applied INTEGER,
    original_value TEXT,
    modified_value TEXT,
    delay_ms INTEGER,
    records_dropped INTEGER
);
```

Do not store sensitive real-world data.

---

# 4.6 Experiment Summary

```sql
CREATE TABLE experiment_summary (
    experiment_id TEXT PRIMARY KEY,
    total_input_records INTEGER,
    total_output_records INTEGER,
    correct_results INTEGER,
    incorrect_results INTEGER,
    attack_attempts INTEGER,
    successful_attacks INTEGER,
    corruption_rate REAL,
    throughput_records_per_second REAL,
    average_latency_ms REAL,
    p95_latency_ms REAL,
    total_processing_time_ms REAL
);
```

---

# 4.7 Future Executor Trust Model

Do not implement yet, but reserve the conceptual model:

```text
ExecutorObservation
```

```text
executor_id
timestamp
task_count
successful_tasks
verification_successes
verification_failures
timeouts
delays
output_mismatches
```

Later:

```text
ExecutorObservation
        ↓
Trust Model
        ↓
Trust Score
```

---

# 5. Folder & Project Structure

```text
spark-byzantine-streaming/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── requirements.txt
│
├── docker/
│   │
│   ├── kafka/
│   │   └── Dockerfile
│   │
│   ├── spark/
│   │   ├── Dockerfile
│   │   └── spark-defaults.conf
│   │
│   └── producer/
│       └── Dockerfile
│
├── config/
│   ├── app.yaml
│   ├── baseline.yaml
│   ├── value_corruption_05.yaml
│   ├── value_corruption_10.yaml
│   ├── value_corruption_20.yaml
│   ├── value_corruption_50.yaml
│   ├── wrong_aggregation.yaml
│   ├── drop_attack.yaml
│   └── delay_attack.yaml
│
├── producer/
│   ├── __init__.py
│   ├── sensor_producer.py
│   ├── event_generator.py
│   └── kafka_client.py
│
├── streaming/
│   ├── __init__.py
│   ├── streaming_app.py
│   ├── schema.py
│   ├── transformations.py
│   ├── sink.py
│   └── checkpoint.py
│
├── attacks/
│   ├── __init__.py
│   ├── controller.py
│   ├── base_attack.py
│   ├── value_corruption.py
│   ├── wrong_aggregation.py
│   ├── drop_computation.py
│   ├── delay_attack.py
│   └── registry.py
│
├── execution/
│   ├── __init__.py
│   ├── executor_identity.py
│   ├── task_metadata.py
│   └── execution_logger.py
│
├── ground_truth/
│   ├── __init__.py
│   ├── calculator.py
│   ├── validator.py
│   └── comparator.py
│
├── experiments/
│   ├── __init__.py
│   ├── run_experiment.py
│   ├── experiment_manager.py
│   ├── metrics.py
│   └── configs/
│
├── analysis/
│   ├── analyze_results.py
│   ├── generate_metrics.py
│   └── plots.py
│
├── database/
│   ├── schema.sql
│   ├── database.py
│   └── migrations/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── ground_truth/
│
├── output/
│   ├── streaming/
│   ├── experiment_results/
│   ├── logs/
│   └── figures/
│
├── tests/
│   ├── unit/
│   │   ├── test_event_generator.py
│   │   ├── test_attacks.py
│   │   ├── test_ground_truth.py
│   │   └── test_metrics.py
│   │
│   ├── integration/
│   │   ├── test_kafka.py
│   │   ├── test_spark_streaming.py
│   │   └── test_end_to_end.py
│   │
│   └── fixtures/
│
├── docs/
│   ├── architecture.md
│   ├── threat_model.md
│   ├── experiment_protocol.md
│   ├── september_review.md
│   └── future_work.md
│
└── scripts/
    ├── start_cluster.sh
    ├── stop_cluster.sh
    ├── create_topics.sh
    ├── run_baseline.sh
    └── run_attack_experiment.sh
```

## Future structure

Later add:

```text
verification/
trust/
scheduler/
replication/
```

Do not implement those modules during the current phase unless needed as empty interfaces/placeholders.

---

# 6. Step-by-Step Implementation Roadmap (ordered logically from setup to core features)

## Phase 0 — Establish Project Conventions

### Step 0.1 — Create repository

Initialize Git.

Create:

```text
main
develop
feature/*
```

branches if appropriate.

### Step 0.2 — Add `.gitignore`

Exclude:

```text
__pycache__
*.pyc
.venv
.env
output/
data/generated/
checkpoints/
logs/
*.db
```

Do not commit generated experiment output unless intentionally selected as a reproducibility artifact.

### Step 0.3 — Create README

Document:

* project objective,
* architecture,
* installation,
* cluster startup,
* Kafka setup,
* baseline experiment,
* attack experiment,
* result analysis.

---

# Phase 1 — Environment Setup

## Step 1.1 — Create Docker Compose

Create services:

```text
kafka
spark-master
spark-worker-1
spark-worker-2
spark-worker-3
```

Ensure services communicate over a private Docker network.

## Step 1.2 — Configure Spark Master

Expose:

```text
7077
8080
```

where appropriate.

## Step 1.3 — Configure workers

Each worker must have:

```text
SPARK_WORKER_CORES
SPARK_WORKER_MEMORY
```

and stable names.

## Step 1.4 — Verify Spark

Open Spark UI and confirm all workers are registered.

Acceptance:

```text
3 workers visible
```

## Step 1.5 — Verify Kafka

Create:

```text
sensor-stream
```

and verify producer/consumer connectivity.

---

# Phase 2 — Implement Event Generator

## Step 2.1

Implement:

```text
event_generator.py
```

Generate deterministic sensor data.

## Step 2.2

Add:

```text
random_seed
```

## Step 2.3

Add configurable:

```text
events_per_second
total_events
sensor_count
temperature_range
humidity_range
```

## Step 2.4

Publish JSON to Kafka.

## Step 2.5

Add producer metrics.

Example:

```text
Produced: 10,000
Duration: 25.2 sec
Rate: 396.8 events/sec
```

---

# Phase 3 — Implement Baseline Spark Streaming

## Step 3.1 — Define schema

Explicitly define:

```text
event_id: long
timestamp: timestamp
sensor_id: string
temperature: double
humidity: double
```

Do not infer schema dynamically for the research baseline.

## Step 3.2 — Read Kafka

Implement:

```text
spark.readStream
    .format("kafka")
```

## Step 3.3 — Parse JSON

Convert Kafka values into structured columns.

## Step 3.4 — Validate records

Track:

```text
valid records
invalid records
```

## Step 3.5 — Transform

Implement a deterministic computation.

Recommended initial computation:

```text
windowed average temperature per sensor
```

Also calculate:

```text
count
min
max
```

## Step 3.6 — Configure checkpointing

Use a unique checkpoint directory per experiment.

Example:

```text
/checkpoints/<experiment_id>
```

## Step 3.7 — Write output

Use a deterministic research-friendly sink.

Store:

```text
batch_id
window_start
window_end
sensor_id
count
avg_temperature
min_temperature
max_temperature
```

---

# Phase 4 — Baseline Validation

Before implementing attacks, freeze the baseline.

## Step 4.1

Run:

```text
10,000 events
3 workers
attack disabled
```

## Step 4.2

Record:

```text
throughput
latency
batch processing time
output count
correctness
```

## Step 4.3

Run the same experiment at least three times.

Calculate:

```text
mean
standard deviation
```

Do not rely on one run.

## Step 4.4

Store:

```text
baseline experiment configuration
baseline raw data
baseline metrics
baseline plots
```

This becomes the control group for all later experiments.

---

# Phase 5 — Implement Executor/Host Identification

Create:

```text
execution/executor_identity.py
```

Capture, where available:

```text
hostname
executor ID
partition ID
task ID
stage ID
batch ID
```

Do not fabricate executor IDs if Spark does not expose them to the chosen execution code.

## Important implementation rule

The system must distinguish:

```text
configured target
```

from:

```text
actual executor identity
```

This prevents misleading experimental claims.

---

# Phase 6 — Implement Byzantine Attack Framework

Create:

```text
BaseAttack
```

with a common interface such as:

```python
apply(context, data)
```

or an equivalent clean abstraction.

Create:

```text
ValueCorruptionAttack
WrongAggregationAttack
DropComputationAttack
DelayAttack
```

Create:

```text
AttackController
```

that decides:

```text
Is attack enabled?
Which attack?
Should this operation be attacked?
Is this executor targeted?
```

---

# Phase 7 — Implement Value Corruption

## Step 7.1

Implement attack probability.

```text
random() < probability
```

## Step 7.2

Implement corruption strategies:

```text
ADD
MULTIPLY
REPLACE
```

## Step 7.3

Record:

```text
original
modified
worker
timestamp
attack type
```

## Step 7.4

Ensure:

```text
probability = 0
```

produces no attack.

## Step 7.5

Ensure:

```text
probability = 1
```

produces an attack whenever an eligible targeted execution occurs.

---

# Phase 8 — Implement Wrong Aggregation

Implement configurable manipulation:

```text
actual + offset
actual × factor
fixed replacement
```

Example:

```yaml
wrong_aggregation:
  strategy: offset
  offset: 20
```

Record both expected and manipulated values.

---

# Phase 9 — Implement Drop Attack

Implement controlled record omission.

Example:

```text
input records = 100
drop probability = 0.20
```

Expected approximate behavior:

```text
processed ≈ 80
dropped ≈ 20
```

Do not expect exactly 20 on every run unless the experiment is explicitly designed deterministically.

---

# Phase 10 — Implement Delay Attack

Implement:

```text
delay_probability
delay_ms
```

Record:

```text
attack start
delay
attack end
```

Measure its effect on:

```text
batch duration
latency
throughput
```

Do not classify slow execution itself as proof of Byzantine behavior.

---

# Phase 11 — Implement Ground Truth

This phase is mandatory before producing research conclusions.

## Step 11.1

Store original input events.

## Step 11.2

Implement an independent calculator.

## Step 11.3

Calculate expected results.

## Step 11.4

Compare Spark output to expected output.

For floating-point values:

```text
abs(actual - expected) <= tolerance
```

rather than direct equality.

## Step 11.5

Generate:

```text
correct
incorrect
absolute error
relative error
```

---

# Phase 12 — Implement Experiment Manager

Create a unified experiment lifecycle:

```text
LOAD CONFIG
     ↓
VALIDATE CONFIG
     ↓
CREATE EXPERIMENT ID
     ↓
START PRODUCER
     ↓
START STREAM
     ↓
COLLECT RESULTS
     ↓
STOP
     ↓
GROUND-TRUTH VALIDATION
     ↓
CALCULATE METRICS
     ↓
SAVE RESULTS
     ↓
GENERATE PLOTS
```

---

# Phase 13 — Implement Baseline Experiment

Configuration:

```yaml
attack:
  enabled: false
```

Run at least:

```text
10,000 records
100 records/sec
500 records/sec
1000 records/sec
```

if the available hardware can sustain those rates.

Measure:

```text
throughput
latency
CPU
memory
correctness
```

---

# Phase 14 — Implement Byzantine Experiment Matrix

Start with one Byzantine attack.

## Experiment Group A

```text
No attack
```

## Experiment Group B

```text
5% corruption
```

## Experiment Group C

```text
10% corruption
```

## Experiment Group D

```text
20% corruption
```

## Experiment Group E

```text
30% corruption
```

## Experiment Group F

```text
50% corruption
```

Then repeat selected configurations for:

```text
wrong aggregation
drop
delay
```

---

# Phase 15 — Repeat Experiments

Every important experiment should have multiple runs.

Recommended:

```text
minimum 3 runs
```

Prefer:

```text
5 runs
```

for final reported results where computational resources permit.

Calculate:

```text
mean
standard deviation
95th percentile latency
```

Do not cherry-pick the best run.

---

# Phase 16 — Generate Research Graphs

Generate at least:

### Graph 1

```text
Attack Probability
vs
Incorrect Result Rate
```

### Graph 2

```text
Attack Probability
vs
Throughput
```

### Graph 3

```text
Attack Probability
vs
Average Latency
```

### Graph 4

```text
Attack Type
vs
Incorrect Results
```

### Graph 5

```text
Attack Type
vs
Latency
```

### Graph 6

```text
Input Rate
vs
Throughput
```

### Graph 7

```text
Input Rate
vs
Latency
```

Use matplotlib.

Do not hard-code colors or fake data.

---

# Phase 17 — Create September Review Report

Generate:

```text
docs/september_review.md
```

Include:

## 1. Problem

Spark provides crash/failure recovery but does not inherently verify arbitrary correctness of successful computation.

## 2. Baseline Architecture

```text
Kafka → Spark → Workers → Output
```

## 3. Threat Model

```text
Normal workers
+
Controlled Byzantine worker
```

## 4. Attack Models

```text
Value corruption
Wrong aggregation
Drop
Delay
```

## 5. Experimental Setup

```text
3 workers
10,000+ events
configured attack rates
```

## 6. Results

Use actual measured values.

## 7. Findings

Explain:

* whether output corruption occurred;
* whether Spark continued processing;
* performance impact;
* which attack types were most disruptive.

## 8. Limitations

Explicitly state:

* controlled simulation rather than real adversarial deployment;
* worker targeting limitations imposed by Spark scheduling;
* no Byzantine consensus;
* no trust mechanism yet;
* no adaptive verification yet.

## 9. Future Work

```text
Adaptive Verification
       ↓
Trust Management
       ↓
Trust-Aware Scheduling
       ↓
Adaptive Replication
```

---

# Phase 18 — Testing

## Unit tests

Test:

```text
event generation
schema validation
attack probability
value corruption
aggregation corruption
drop behavior
delay behavior
ground truth
metric calculation
configuration validation
```

## Integration tests

Test:

```text
Kafka → Spark
Kafka → Spark → Output
Kafka → Spark → Attack → Output
```

## End-to-end test

Run:

```text
Kafka
+
3 Spark workers
+
1 configured attack
+
ground truth
+
metrics
```

and ensure the full experiment completes.

---

# Phase 19 — Final Acceptance Test

The implementation is considered complete for the September milestone only if all of the following are true.

### Infrastructure

* [ ] Docker Compose starts successfully.
* [ ] Kafka is reachable.
* [ ] Spark Master starts.
* [ ] Three workers register.
* [ ] Spark UI displays workers.

### Baseline

* [ ] Producer generates events.
* [ ] Kafka receives events.
* [ ] Spark reads events.
* [ ] Spark performs deterministic computation.
* [ ] Output is persisted.
* [ ] Checkpointing is configured.
* [ ] Ground truth validates baseline output.
* [ ] Baseline performance metrics are collected.

### Byzantine simulation

* [ ] Attack controller works.
* [ ] Value corruption works.
* [ ] Wrong aggregation works.
* [ ] Drop attack works.
* [ ] Delay attack works.
* [ ] Attack probability is configurable.
* [ ] Attack target is configurable.
* [ ] Attack events are logged.

### Evaluation

* [ ] 0% attack experiment works.
* [ ] 5% attack experiment works.
* [ ] 10% attack experiment works.
* [ ] 20% attack experiment works.
* [ ] 30% attack experiment works.
* [ ] 50% attack experiment works.
* [ ] Results are stored.
* [ ] Ground-truth correctness is calculated.
* [ ] Throughput is calculated.
* [ ] Latency is calculated.
* [ ] Graphs are generated.

### Reproducibility

* [ ] Every experiment stores configuration.
* [ ] Every experiment stores random seed.
* [ ] Versions are documented.
* [ ] Experiment IDs are unique.
* [ ] Results can be regenerated.
* [ ] README contains complete setup instructions.

---

# Implementation Agent Constraints

The coding agent must follow these rules throughout implementation:

1. **Do not implement features outside the current milestone unless explicitly requested.**
2. Keep Spark's core source code unmodified.
3. Do not claim deterministic task-to-worker assignment unless the implementation actually guarantees it.
4. Do not fabricate executor IDs, task IDs, or experimental measurements.
5. Do not fabricate performance results.
6. Do not use blockchain or PBFT.
7. Do not introduce Kubernetes.
8. Do not introduce machine learning in the current phase.
9. Keep attack injection completely controlled and local.
10. Make all attack behavior configurable.
11. Keep normal Spark behavior available as an attack-free baseline.
12. Preserve raw experimental data.
13. Never overwrite previous experiment results silently.
14. Give every experiment a unique ID.
15. Record configuration together with results.
16. Use deterministic seeds where randomness is involved.
17. Use independent ground truth for correctness evaluation.
18. Clearly distinguish:

    * task failure,
    * timeout,
    * performance degradation,
    * incorrect computation,
    * deliberately injected Byzantine behavior.
19. Do not label a slow worker as Byzantine merely because it is slow.
20. Do not claim the September prototype provides formal Byzantine fault tolerance.
21. Design interfaces so October's verification module can consume execution/attack observations.
22. Design interfaces so the later trust module can consume worker behavior records.
23. Design interfaces so the eventual scheduler can consume trust scores.
24. Prefer simple, testable components over complex frameworks.
25. Every major module must have unit tests.
26. Every major end-to-end feature must have an integration test.
27. Every experiment must produce machine-readable output.
28. All plots must be generated from actual experiment data.
29. Document assumptions and limitations.
30. Keep the implementation suitable for a one-year BTech CSE research project.

## Future Research Pipeline — Do Not Implement Yet

The architecture must ultimately evolve into:

```text
                    Kafka
                      │
                      ▼
             Spark Structured Streaming
                      │
                      ▼
              Distributed Execution
                      │
          ┌───────────┴───────────┐
          │                       │
     Normal Worker          Suspicious Worker
          │                       │
          └───────────┬───────────┘
                      ▼
             Adaptive Verification
                      │
             ┌────────┴────────┐
             │                 │
          Match             Mismatch
             │                 │
             ▼                 ▼
        Positive          Negative Evidence
             │                 │
             └────────┬────────┘
                      ▼
                Trust Manager
                      │
                      ▼
                Trust Scores
                      │
                      ▼
             Adaptive Scheduler
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      High Trust   Medium Trust  Low Trust
       Normal       Verify More   Replicate/
       Tasks         Often        Quarantine
                      │
                      ▼
               Updated Evidence
                      │
                      └──────────► Trust Manager
```

The **September implementation is the experimental foundation of this complete loop**. It must therefore prioritize clean measurement, reproducibility, ground-truth correctness, and controlled Byzantine injection over complexity.
