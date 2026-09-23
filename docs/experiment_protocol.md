# Experiment Protocol & Methodology

## 1. Experimental Matrix

Every experiment configuration runs against a 10,000-event synthetic dataset over 3 Spark worker nodes.

| Experiment Config | Attack Type | Probability | Target Worker |
|-------------------|-------------|-------------|---------------|
| `baseline.yaml` | NONE | 0% | None |
| `value_corruption_05.yaml` | VALUE_CORRUPTION | 5% | spark-worker-3 |
| `value_corruption_10.yaml` | VALUE_CORRUPTION | 10% | spark-worker-3 |
| `value_corruption_20.yaml` | VALUE_CORRUPTION | 20% | spark-worker-3 |
| `value_corruption_30.yaml` | VALUE_CORRUPTION | 30% | spark-worker-3 |
| `value_corruption_50.yaml` | VALUE_CORRUPTION | 50% | spark-worker-3 |
| `wrong_aggregation.yaml` | WRONG_AGGREGATION | 20% | spark-worker-3 |
| `drop_attack.yaml` | DROP_COMPUTATION | 20% | spark-worker-3 |
| `delay_attack.yaml` | DELAY | 20% | spark-worker-3 |

## 2. Evaluation Metrics

- **Correctness**: Absolute error, relative error, accuracy rate, corruption rate.
- **Performance**: Throughput (records/sec), average latency (ms), p95 latency (ms).
- **Reproduction**: Seed `42`, saved `config.yaml`, unique `experiment_id`.
