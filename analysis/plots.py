import matplotlib
matplotlib.use('Agg')  # Headless rendering
import matplotlib.pyplot as plt
import os
import json
from pathlib import Path
from typing import List, Dict, Any

class ExperimentPlotter:
    """Generates research visualization plots from experiment metrics data."""

    def __init__(self, output_dir: str = "output/figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use('ggplot')

    def generate_all_plots(self, experiment_summaries: List[Dict[str, Any]]):
        """Generate full suite of experiment charts from collected summaries."""
        if not experiment_summaries:
            return

        self.plot_attack_prob_vs_corruption(experiment_summaries)
        self.plot_attack_prob_vs_throughput(experiment_summaries)
        self.plot_attack_prob_vs_latency(experiment_summaries)
        self.plot_attack_type_vs_incorrect(experiment_summaries)
        self.plot_attack_type_vs_latency(experiment_summaries)
        self.plot_input_rate_vs_throughput(experiment_summaries)
        self.plot_input_rate_vs_latency(experiment_summaries)

    def plot_attack_prob_vs_corruption(self, summaries: List[Dict[str, Any]]):
        probs = [s.get("attack_probability", 0.0) * 100 for s in summaries]
        corruptions = [s.get("corruption_rate", 0.0) * 100 for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.plot(probs, corruptions, marker='o', color='#d9534f', linewidth=2)
        plt.title("Attack Probability vs Incorrect-Result Rate")
        plt.xlabel("Configured Attack Probability (%)")
        plt.ylabel("Incorrect Result Rate (%)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot1_attack_prob_vs_corruption.png")
        plt.close()

    def plot_attack_prob_vs_throughput(self, summaries: List[Dict[str, Any]]):
        probs = [s.get("attack_probability", 0.0) * 100 for s in summaries]
        tp = [s.get("throughput_records_per_second", 0.0) for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.plot(probs, tp, marker='s', color='#0275d8', linewidth=2)
        plt.title("Attack Probability vs Processing Throughput")
        plt.xlabel("Configured Attack Probability (%)")
        plt.ylabel("Throughput (records/sec)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot2_attack_prob_vs_throughput.png")
        plt.close()

    def plot_attack_prob_vs_latency(self, summaries: List[Dict[str, Any]]):
        probs = [s.get("attack_probability", 0.0) * 100 for s in summaries]
        avg_lat = [s.get("average_latency_ms", 0.0) for s in summaries]
        p95_lat = [s.get("p95_latency_ms", 0.0) for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.plot(probs, avg_lat, marker='o', label="Avg Latency (ms)", color='#f0ad4e')
        plt.plot(probs, p95_lat, marker='^', label="p95 Latency (ms)", color='#5bc0de')
        plt.title("Attack Probability vs Batch Latency")
        plt.xlabel("Configured Attack Probability (%)")
        plt.ylabel("Latency (ms)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot3_attack_prob_vs_latency.png")
        plt.close()

    def plot_attack_type_vs_incorrect(self, summaries: List[Dict[str, Any]]):
        types = [s.get("attack_type", "NONE") for s in summaries]
        incorrects = [s.get("incorrect_results", 0) for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.bar(types, incorrects, color='#5cb85c')
        plt.title("Attack Type vs Incorrect Results Count")
        plt.xlabel("Attack Type")
        plt.ylabel("Incorrect Output Records")
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot4_attack_type_vs_incorrect.png")
        plt.close()

    def plot_attack_type_vs_latency(self, summaries: List[Dict[str, Any]]):
        types = [s.get("attack_type", "NONE") for s in summaries]
        avg_lat = [s.get("average_latency_ms", 0.0) for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.bar(types, avg_lat, color='#d9534f')
        plt.title("Attack Type vs Average Processing Latency")
        plt.xlabel("Attack Type")
        plt.ylabel("Average Latency (ms)")
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot5_attack_type_vs_latency.png")
        plt.close()

    def plot_input_rate_vs_throughput(self, summaries: List[Dict[str, Any]]):
        rates = [s.get("input_rate", 500) for s in summaries]
        tp = [s.get("throughput_records_per_second", 0.0) for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.scatter(rates, tp, color='#0275d8', s=100)
        plt.title("Input Event Rate vs Measured Throughput")
        plt.xlabel("Configured Input Rate (events/sec)")
        plt.ylabel("Measured Throughput (records/sec)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot6_input_rate_vs_throughput.png")
        plt.close()

    def plot_input_rate_vs_latency(self, summaries: List[Dict[str, Any]]):
        rates = [s.get("input_rate", 500) for s in summaries]
        avg_lat = [s.get("average_latency_ms", 0.0) for s in summaries]

        plt.figure(figsize=(8, 5))
        plt.scatter(rates, avg_lat, color='#f0ad4e', s=100)
        plt.title("Input Event Rate vs Measured Latency")
        plt.xlabel("Configured Input Rate (events/sec)")
        plt.ylabel("Average Latency (ms)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output_dir / "plot7_input_rate_vs_latency.png")
        plt.close()
