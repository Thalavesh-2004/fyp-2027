import argparse
import sys
import logging
from experiments.experiment_manager import ExperimentManager

def main():
    parser = argparse.ArgumentParser(description="Run Apache Spark Byzantine Streaming Experiment")
    parser.add_argument("--config", required=True, help="Path to experiment YAML configuration file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("run_experiment")

    logger.info(f"Loading configuration: {args.config}")
    try:
        manager = ExperimentManager(args.config)
        summary = manager.run()
        print("\n=== Experiment Summary ===")
        print(f"ID: {summary['experiment_id']}")
        print(f"Throughput: {summary['throughput_records_per_second']} rec/s")
        print(f"Avg Latency: {summary['average_latency_ms']} ms")
        print(f"Correctness Rate: {(1.0 - summary['corruption_rate'])*100:.2f}%")
        print(f"Corruption Rate: {summary['corruption_rate']*100:.2f}%")
        print("===========================\n")
    except Exception as e:
        logger.error(f"Experiment execution failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
