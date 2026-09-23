# Threat Model Specification

## 1. Problem Definition

Apache Spark Structured Streaming handles node failures and crashes through lineage recovery and checkpointing. However, standard failure recovery assumes that any successfully executed task yields semantically correct outputs. 

A **Byzantine worker** remains operational and returns task success responses to the Spark master, but produces manipulated, omitted, or delayed computation outputs.

## 2. Injected Attack Modes

1. **Value Corruption (`VALUE_CORRUPTION`)**:
   - Modifies raw sensor values (e.g. adding +50.0 to temperature).
   - Demonstrates semantic corruption without process crash.

2. **Wrong Aggregation (`WRONG_AGGREGATION`)**:
   - Returns mathematically altered aggregate values (e.g. average temperature offset by +25.0).

3. **Drop Computation (`DROP_COMPUTATION`)**:
   - Selectively omits input events or computation tasks.

4. **Delay Attack (`DELAY`)**:
   - Introduces controlled processing latency (e.g. 2000 ms sleep).

## 3. Scope & Safety Constraints

All fault injections are strictly controlled via YAML configurations, local to the Docker testbed environment, and fully reproducible via random seeds.
