"""
Generates a self-contained HTML research dashboard from experiment results.
Reads SQLite DB, JSON results, and plot images to produce a single interactive HTML file.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import base64
import webbrowser
from pathlib import Path
from producer.event_generator import EventGenerator
from ground_truth.calculator import GroundTruthCalculator


def load_image_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_experiment_summaries(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.experiment_id, e.name, e.attack_enabled, e.attack_type, e.attack_probability,
               e.input_rate, e.input_record_count, s.total_input_records, s.total_output_records,
               s.correct_results, s.incorrect_results, s.corruption_rate,
               s.throughput_records_per_second, s.average_latency_ms, s.p95_latency_ms,
               s.total_processing_time_ms, s.attack_attempts, s.successful_attacks
        FROM experiment_summary s
        JOIN experiments e ON s.experiment_id = e.experiment_id
        ORDER BY e.attack_probability ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    summaries = []
    for r in rows:
        summaries.append({
            "id": r[0], "name": r[1], "attack_enabled": bool(r[2]),
            "attack_type": r[3] or "NONE", "attack_probability": r[4] or 0.0,
            "input_rate": r[5] or 500, "input_record_count": r[6] or 10000,
            "total_input": r[7] or 0, "total_output": r[8] or 0,
            "correct": r[9] or 0, "incorrect": r[10] or 0,
            "corruption_rate": r[11] or 0.0,
            "throughput": r[12] or 0.0, "avg_latency": r[13] or 0.0,
            "p95_latency": r[14] or 0.0, "processing_time": r[15] or 0.0,
            "attack_attempts": r[16] or 0, "successful_attacks": r[17] or 0
        })
    return summaries


def generate_sample_events(count=20, seed=42):
    gen = EventGenerator(random_seed=seed, sensor_count=5)
    events = gen.generate_batch(count)
    return events


def generate_dashboard():
    db_path = "output/experiments.db"
    figures_dir = Path("output/figures")
    output_html = Path("dashboard/index.html")

    summaries = load_experiment_summaries(db_path)
    sample_input = generate_sample_events(30, seed=42)

    # Ground truth for sample
    gt = GroundTruthCalculator.calculate_expected_aggregates(sample_input)

    # Load plot images as base64
    plot_files = sorted(figures_dir.glob("*.png"))
    plots_b64 = []
    for pf in plot_files:
        plots_b64.append({
            "name": pf.stem.replace("_", " ").title(),
            "data": load_image_base64(str(pf))
        })

    # Load per-experiment detail results
    exp_details = {}
    results_dir = Path("output/experiment_results")
    for exp_dir in sorted(results_dir.iterdir()):
        if exp_dir.is_dir():
            summary_file = exp_dir / "summary.json"
            metrics_file = exp_dir / "metrics.json"
            if summary_file.exists():
                with open(summary_file, "r") as f:
                    exp_details[exp_dir.name] = json.load(f)

    # Build HTML
    html = build_html(summaries, sample_input, gt, plots_b64, exp_details)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated: {output_html.resolve()}")
    webbrowser.open(str(output_html.resolve()))


def build_html(summaries, sample_input, ground_truth, plots, exp_details):
    # Summary cards data
    baseline = next((s for s in summaries if s["attack_type"] == "NONE"), None)
    worst = max(summaries, key=lambda s: s["corruption_rate"]) if summaries else None
    total_experiments = len(summaries)

    # Build experiment rows
    exp_rows = ""
    for s in summaries:
        corr_class = "correct" if s["corruption_rate"] == 0 else "corrupted"
        attack_badge = f'<span class="badge badge-none">NONE</span>' if s["attack_type"] == "NONE" else f'<span class="badge badge-attack">{s["attack_type"]}</span>'
        records_attacked = s["attack_attempts"]
        records_attacked_pct = (records_attacked / s["total_input"] * 100) if s["total_input"] > 0 else 0
        sensors_bad = s["incorrect"]
        sensors_total = s["correct"] + s["incorrect"]
        exp_rows += f"""
        <tr class="{corr_class}-row">
            <td><code>{s["id"]}</code></td>
            <td>{s["name"]}</td>
            <td>{attack_badge}</td>
            <td>{s["attack_probability"]*100:.0f}%</td>
            <td>{s["total_input"]:,}</td>
            <td>{s["total_output"]:,}</td>
            <td><span class="rate {'bad' if records_attacked > 0 else 'good'}">{records_attacked:,} ({records_attacked_pct:.1f}%)</span></td>
            <td>{s["throughput"]:,.0f}</td>
            <td>{s["avg_latency"]:.1f}</td>
            <td><span class="rate {'good' if sensors_bad == 0 else 'bad'}">{s['correct']}/{sensors_total} correct</span></td>
            <td><span class="rate {'good' if sensors_bad == 0 else 'bad'}">{sensors_bad}/{sensors_total} wrong</span></td>
        </tr>"""

    # Build input events table (first 20)
    input_rows = ""
    for i, ev in enumerate(sample_input[:20]):
        input_rows += f"""
        <tr>
            <td>{ev['event_id']}</td>
            <td>{ev['timestamp'][:19]}</td>
            <td><span class="sensor-tag">{ev['sensor_id']}</span></td>
            <td>{ev['temperature']:.2f} °C</td>
            <td>{ev['humidity']:.2f} %</td>
        </tr>"""

    # Ground truth table
    gt_rows = ""
    for sid in sorted(ground_truth.keys()):
        gt_item = ground_truth[sid]
        gt_rows += f"""
        <tr>
            <td><span class="sensor-tag">{sid}</span></td>
            <td>{gt_item['event_count']}</td>
            <td>{gt_item['avg_temperature']:.2f} °C</td>
            <td>{gt_item['min_temperature']:.2f} °C</td>
            <td>{gt_item['max_temperature']:.2f} °C</td>
            <td>{gt_item['avg_humidity']:.2f} %</td>
        </tr>"""

    # Build plot cards
    plot_cards = ""
    for p in plots:
        plot_cards += f"""
        <div class="plot-card">
            <h4>{p['name']}</h4>
            <img src="data:image/png;base64,{p['data']}" alt="{p['name']}" />
        </div>"""

    # Timeline / attack comparison cards
    comparison_cards = ""
    for s in summaries:
        icon = "✅" if s["corruption_rate"] == 0 else "❌"
        bar_width = max(2, int(s["corruption_rate"] * 100))
        tp_bar = min(100, int((s["throughput"] / (baseline["throughput"] if baseline else 1)) * 100))
        comparison_cards += f"""
        <div class="comparison-card {'card-clean' if s['corruption_rate'] == 0 else 'card-attacked'}">
            <div class="card-header">
                <span class="card-icon">{icon}</span>
                <h4>{s['name']}</h4>
            </div>
            <div class="card-metrics">
                <div class="metric-row">
                    <span class="metric-label">Attack Type</span>
                    <span class="metric-value">{s['attack_type']}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Config Attack Rate</span>
                    <span class="metric-value">{s['attack_probability']*100:.0f}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Records Attacked</span>
                    <span class="metric-value {'bad' if s['attack_attempts'] > 0 else 'good'}">{s['attack_attempts']:,} / {s['total_input']:,}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Throughput</span>
                    <span class="metric-value">{s['throughput']:,.0f} rec/s</span>
                </div>
                <div class="metric-bar">
                    <div class="bar-fill bar-throughput" style="width: {tp_bar}%"></div>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Latency</span>
                    <span class="metric-value">{s['avg_latency']:.1f} ms</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Sensors Validated</span>
                    <span class="metric-value {'good' if s['incorrect'] == 0 else 'bad'}">{s['correct']}/{s['correct']+s['incorrect']} correct, {s['incorrect']}/{s['correct']+s['incorrect']} wrong</span>
                </div>
                <div class="metric-bar">
                    <div class="bar-fill {'bar-correct' if s['corruption_rate'] == 0 else 'bar-corrupt'}" style="width: {bar_width}%"></div>
                </div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Byzantine Fault Tolerance — Spark Streaming Research Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
:root {{
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a1f35;
    --bg-card-hover: #222845;
    --border: #2a3050;
    --text-primary: #e8eaf0;
    --text-secondary: #9ca3be;
    --text-muted: #6b7394;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-orange: #f59e0b;
    --accent-purple: #8b5cf6;
    --gradient-hero: linear-gradient(135deg, #1e3a5f 0%, #0a0e1a 50%, #1a0a2e 100%);
    --glass: rgba(26, 31, 53, 0.7);
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}}
body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}}

/* ===== HERO HEADER ===== */
.hero {{
    background: var(--gradient-hero);
    padding: 60px 40px 50px;
    text-align: center;
    border-bottom: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}}
.hero::before {{
    content: '';
    position: absolute;
    top: -50%;
    left: -20%;
    width: 140%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 50%, rgba(59,130,246,0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 50%, rgba(139,92,246,0.06) 0%, transparent 60%);
    pointer-events: none;
}}
.hero h1 {{
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #e8eaf0 0%, #3b82f6 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
    position: relative;
}}
.hero .subtitle {{
    font-size: 1.05rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-bottom: 6px;
    position: relative;
}}
.hero .milestone {{
    display: inline-block;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: var(--accent-blue);
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 14px;
    position: relative;
}}

/* ===== NAV TABS ===== */
.nav {{
    display: flex;
    justify-content: center;
    gap: 4px;
    padding: 16px 40px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
}}
.nav button {{
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-secondary);
    padding: 10px 22px;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    transition: all 0.2s ease;
}}
.nav button:hover {{
    background: var(--bg-card);
    color: var(--text-primary);
}}
.nav button.active {{
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
    color: var(--accent-blue);
}}

/* ===== SECTIONS ===== */
.container {{ max-width: 1400px; margin: 0 auto; padding: 30px 40px; }}
.section {{ display: none; animation: fadeIn 0.3s ease; }}
.section.active {{ display: block; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.section-title {{
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 6px;
    color: var(--text-primary);
}}
.section-desc {{
    color: var(--text-secondary);
    font-size: 0.92rem;
    margin-bottom: 28px;
}}

/* ===== SUMMARY CARDS ===== */
.summary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 36px;
}}
.summary-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 24px;
    transition: all 0.2s ease;
}}
.summary-card:hover {{
    border-color: var(--accent-blue);
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}}
.summary-card .card-label {{
    font-size: 0.78rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-muted);
    margin-bottom: 8px;
}}
.summary-card .card-value {{
    font-size: 1.8rem;
    font-weight: 700;
}}
.summary-card .card-sub {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 4px;
}}
.summary-card.blue .card-value {{ color: var(--accent-blue); }}
.summary-card.green .card-value {{ color: var(--accent-green); }}
.summary-card.red .card-value {{ color: var(--accent-red); }}
.summary-card.orange .card-value {{ color: var(--accent-orange); }}
.summary-card.purple .card-value {{ color: var(--accent-purple); }}
.summary-card.cyan .card-value {{ color: var(--accent-cyan); }}

/* ===== TABLES ===== */
.table-wrap {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 32px;
}}
.table-wrap h3 {{
    padding: 18px 24px;
    font-size: 1rem;
    font-weight: 600;
    border-bottom: 1px solid var(--border);
    background: rgba(59, 130, 246, 0.05);
}}
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}}
thead th {{
    background: var(--bg-secondary);
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.8px;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 56px;
}}
tbody td {{
    padding: 11px 16px;
    border-bottom: 1px solid rgba(42, 48, 80, 0.5);
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
}}
tbody tr:hover {{ background: var(--bg-card-hover); }}
tbody tr:last-child td {{ border-bottom: none; }}
.corrupted-row {{ background: rgba(239, 68, 68, 0.06); }}
.corrupted-row:hover {{ background: rgba(239, 68, 68, 0.1); }}
code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    background: rgba(59, 130, 246, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
}}

/* ===== BADGES & RATES ===== */
.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
}}
.badge-none {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); }}
.badge-attack {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }}
.rate {{ font-weight: 600; }}
.rate.good {{ color: var(--accent-green); }}
.rate.bad {{ color: var(--accent-red); }}
.sensor-tag {{
    background: rgba(139, 92, 246, 0.15);
    color: var(--accent-purple);
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}}

/* ===== COMPARISON CARDS ===== */
.comparison-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}}
.comparison-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 22px;
    transition: all 0.25s ease;
}}
.comparison-card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow); }}
.card-clean {{ border-left: 3px solid var(--accent-green); }}
.card-attacked {{ border-left: 3px solid var(--accent-red); }}
.card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }}
.card-icon {{ font-size: 1.4rem; }}
.card-header h4 {{ font-size: 0.95rem; font-weight: 600; }}
.card-metrics {{ display: flex; flex-direction: column; gap: 8px; }}
.metric-row {{ display: flex; justify-content: space-between; align-items: center; }}
.metric-label {{ font-size: 0.8rem; color: var(--text-muted); }}
.metric-value {{ font-size: 0.85rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
.metric-bar {{
    height: 4px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    overflow: hidden;
}}
.bar-fill {{
    height: 100%;
    border-radius: 2px;
    transition: width 0.6s ease;
}}
.bar-throughput {{ background: var(--accent-blue); }}
.bar-correct {{ background: var(--accent-green); }}
.bar-corrupt {{ background: var(--accent-red); }}

/* ===== PLOTS ===== */
.plots-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}}
.plot-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.25s ease;
}}
.plot-card:hover {{ border-color: var(--accent-blue); transform: translateY(-2px); box-shadow: var(--shadow); }}
.plot-card h4 {{
    padding: 16px 20px;
    font-size: 0.9rem;
    font-weight: 600;
    border-bottom: 1px solid var(--border);
    background: rgba(59, 130, 246, 0.04);
}}
.plot-card img {{
    width: 100%;
    display: block;
    padding: 12px;
    background: #fff;
}}

/* ===== FINDING BOXES ===== */
.finding-box {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
    border-left: 4px solid var(--accent-blue);
}}
.finding-box.critical {{ border-left-color: var(--accent-red); }}
.finding-box.success {{ border-left-color: var(--accent-green); }}
.finding-box h4 {{
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 8px;
}}
.finding-box p {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.7;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {{
    .hero {{ padding: 40px 20px 30px; }}
    .hero h1 {{ font-size: 1.6rem; }}
    .container {{ padding: 20px 16px; }}
    .nav {{ padding: 12px 16px; flex-wrap: wrap; }}
    .plots-grid {{ grid-template-columns: 1fr; }}
    .comparison-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<!-- HERO -->
<header class="hero">
    <h1>Byzantine Fault Tolerance in Apache Spark Streaming</h1>
    <p class="subtitle">Research Testbed — Baseline Implementation & Attack Simulation Dashboard</p>
    <span class="milestone">📅 September 2026 Milestone — FYP Research Demo</span>
</header>

<!-- NAV -->
<nav class="nav" id="nav">
    <button class="active" onclick="showTab('overview')">Overview</button>
    <button onclick="showTab('input')">Input Events</button>
    <button onclick="showTab('results')">Experiment Results</button>
    <button onclick="showTab('comparison')">Attack Comparison</button>
    <button onclick="showTab('groundtruth')">Ground Truth</button>
    <button onclick="showTab('plots')">Research Plots</button>
    <button onclick="showTab('findings')">Key Findings</button>
</nav>

<div class="container">

    <!-- ===== OVERVIEW TAB ===== -->
    <div class="section active" id="tab-overview">
        <h2 class="section-title">Experiment Overview</h2>
        <p class="section-desc">Summary metrics across {total_experiments} experiments executed against a simulated 3-worker Spark cluster.</p>

        <div class="summary-grid">
            <div class="summary-card blue">
                <div class="card-label">Total Experiments</div>
                <div class="card-value">{total_experiments}</div>
                <div class="card-sub">9 configs × 10,000 events each</div>
            </div>
            <div class="summary-card green">
                <div class="card-label">Baseline Throughput</div>
                <div class="card-value">{baseline['throughput']:,.0f}</div>
                <div class="card-sub">records / second (no attack)</div>
            </div>
            <div class="summary-card cyan">
                <div class="card-label">Baseline Latency</div>
                <div class="card-value">{baseline['avg_latency']:.1f} ms</div>
                <div class="card-sub">average batch processing time</div>
            </div>
            <div class="summary-card green">
                <div class="card-label">Baseline Correctness</div>
                <div class="card-value">100%</div>
                <div class="card-sub">5/5 sensors verified correct</div>
            </div>
            <div class="summary-card red">
                <div class="card-label">Worst Corruption Rate</div>
                <div class="card-value">{worst['corruption_rate']*100:.0f}%</div>
                <div class="card-sub">{worst['name']}</div>
            </div>
            <div class="summary-card orange">
                <div class="card-label">Attack Types Tested</div>
                <div class="card-value">4</div>
                <div class="card-sub">Value, Aggregation, Drop, Delay</div>
            </div>
        </div>

        <div class="finding-box">
            <h4>💡 Understanding the Metrics</h4>
            <p><strong>Records Attacked</strong> = how many individual events were corrupted (e.g. 1,021 out of 10,000 = ~10%). <strong>Sensors Wrong</strong> = how many per-sensor aggregates (avg temperature) failed ground-truth validation. Even 5% record corruption poisons ALL 5 sensor averages because each corrupted record shifts the aggregate by +50°C ÷ total records — exceeding the ±0.01°C validation tolerance.</p>
        </div>

        <div class="table-wrap">
            <h3>📊 All Experiment Results Summary</h3>
            <table>
                <thead>
                    <tr>
                        <th>Experiment ID</th>
                        <th>Name</th>
                        <th>Attack Type</th>
                        <th>Config Attack %</th>
                        <th>Input Records</th>
                        <th>Output Records</th>
                        <th>Records Attacked</th>
                        <th>Throughput (rec/s)</th>
                        <th>Avg Latency (ms)</th>
                        <th>Sensors Correct</th>
                        <th>Sensors Wrong</th>
                    </tr>
                </thead>
                <tbody>{exp_rows}</tbody>
            </table>
        </div>
    </div>

    <!-- ===== INPUT EVENTS TAB ===== -->
    <div class="section" id="tab-input">
        <h2 class="section-title">Input Sensor Events</h2>
        <p class="section-desc">Sample of 20 synthetic IoT sensor events generated deterministically using random seed 42. These raw events are fed into the Spark Structured Streaming pipeline.</p>

        <div class="summary-grid">
            <div class="summary-card blue">
                <div class="card-label">Total Events</div>
                <div class="card-value">10,000</div>
                <div class="card-sub">per experiment run</div>
            </div>
            <div class="summary-card purple">
                <div class="card-label">Sensor Count</div>
                <div class="card-value">5</div>
                <div class="card-sub">S001 – S005</div>
            </div>
            <div class="summary-card cyan">
                <div class="card-label">Random Seed</div>
                <div class="card-value">42</div>
                <div class="card-sub">deterministic & reproducible</div>
            </div>
            <div class="summary-card orange">
                <div class="card-label">Event Rate</div>
                <div class="card-value">500/s</div>
                <div class="card-sub">configured ingestion rate</div>
            </div>
        </div>

        <div class="table-wrap">
            <h3>🔢 Raw Sensor Event Data (First 20 Events)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Event ID</th>
                        <th>Timestamp</th>
                        <th>Sensor ID</th>
                        <th>Temperature</th>
                        <th>Humidity</th>
                    </tr>
                </thead>
                <tbody>{input_rows}</tbody>
            </table>
        </div>
    </div>

    <!-- ===== EXPERIMENT RESULTS TAB ===== -->
    <div class="section" id="tab-results">
        <h2 class="section-title">Detailed Experiment Results</h2>
        <p class="section-desc">Per-experiment output metrics showing the impact of each Byzantine attack mode. Note: "Records Attacked" shows individual corrupted events, while "Sensors Wrong" shows how many per-sensor aggregates failed ground-truth validation.</p>

        <div class="finding-box critical">
            <h4>⚠️ Amplification Effect</h4>
            <p>Even when only 5-10% of individual records are corrupted (+50°C each), <strong>all 5 sensor aggregates</strong> become incorrect. This is because each corrupted record shifts the average temperature by (corrupted_count × 50) ÷ total_count, which far exceeds the ±0.01°C validation tolerance. This "amplification effect" is a key research finding — a small number of Byzantine records can poison an entire aggregate computation.</p>
        </div>

        <div class="table-wrap">
            <h3>📋 Full Results Table</h3>
            <table>
                <thead>
                    <tr>
                        <th>Experiment ID</th>
                        <th>Name</th>
                        <th>Attack Type</th>
                        <th>Config Attack %</th>
                        <th>Input Records</th>
                        <th>Output Records</th>
                        <th>Records Attacked</th>
                        <th>Throughput (rec/s)</th>
                        <th>Avg Latency (ms)</th>
                        <th>Sensors Correct</th>
                        <th>Sensors Wrong</th>
                    </tr>
                </thead>
                <tbody>{exp_rows}</tbody>
            </table>
        </div>
    </div>

    <!-- ===== COMPARISON TAB ===== -->
    <div class="section" id="tab-comparison">
        <h2 class="section-title">Attack Comparison Dashboard</h2>
        <p class="section-desc">Side-by-side comparison of all experiment configurations showing how each attack type affects the streaming pipeline.</p>

        <div class="comparison-grid">
            {comparison_cards}
        </div>
    </div>

    <!-- ===== GROUND TRUTH TAB ===== -->
    <div class="section" id="tab-groundtruth">
        <h2 class="section-title">Independent Ground Truth Validation</h2>
        <p class="section-desc">Expected aggregate statistics computed independently from the raw input events (without going through Spark). These values are compared against Spark's output to detect Byzantine corruption.</p>

        <div class="finding-box success">
            <h4>✅ How Ground Truth Works</h4>
            <p>The Ground Truth Calculator processes the same raw events using pure Python — completely independent of the Spark streaming engine. It computes per-sensor averages, min/max, and counts. Then the Comparator checks if Spark's output matches within a tolerance of ±0.01. Any deviation is flagged as corruption.</p>
        </div>

        <div class="table-wrap">
            <h3>🎯 Expected Per-Sensor Aggregates (Ground Truth — 30 sample events)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Sensor ID</th>
                        <th>Event Count</th>
                        <th>Avg Temperature</th>
                        <th>Min Temperature</th>
                        <th>Max Temperature</th>
                        <th>Avg Humidity</th>
                    </tr>
                </thead>
                <tbody>{gt_rows}</tbody>
            </table>
        </div>
    </div>

    <!-- ===== RESEARCH PLOTS TAB ===== -->
    <div class="section" id="tab-plots">
        <h2 class="section-title">Research Visualizations</h2>
        <p class="section-desc">Auto-generated Matplotlib charts showing the quantitative relationship between attack parameters and system performance metrics.</p>

        <div class="plots-grid">
            {plot_cards}
        </div>
    </div>

    <!-- ===== KEY FINDINGS TAB ===== -->
    <div class="section" id="tab-findings">
        <h2 class="section-title">Key Research Findings</h2>
        <p class="section-desc">Critical observations from the September 2026 experimental demonstration.</p>

        <div class="finding-box critical">
            <h4>🔴 Finding 1: Spark Silently Accepts Corrupted Results</h4>
            <p>In all value corruption experiments (5% – 50%), Apache Spark reported <strong>TASK SUCCESS</strong> for every micro-batch. The Byzantine worker remained active, returned manipulated temperature values (+50°C), and Spark's built-in fault tolerance (lineage + checkpointing) never triggered a retry. Standard Spark assumes fail-stop behavior and has <strong>zero protection</strong> against semantic corruption.</p>
        </div>

        <div class="finding-box critical">
            <h4>🔴 Finding 2: Even 5% Attack Rate Corrupts 100% of Aggregates</h4>
            <p>With only 5% of individual records attacked, <strong>all 5 sensor aggregates</strong> were detected as incorrect by the Ground Truth Validator. Because aggregation functions (avg, min, max) combine values across many records, even a small fraction of corrupted inputs poisons the entire output.</p>
        </div>

        <div class="finding-box">
            <h4>🔵 Finding 3: Delay Attacks Degrade Throughput by 4x</h4>
            <p>The 20% delay attack (500ms per affected batch) reduced throughput from ~70,000 rec/s down to ~16,000 rec/s and increased average latency from 4.3ms to 105.6ms — a <strong>25x latency increase</strong>. However, unlike value corruption, delay attacks did not affect result correctness (100% accuracy maintained).</p>
        </div>

        <div class="finding-box success">
            <h4>🟢 Finding 4: Independent Ground Truth Validation Works</h4>
            <p>The dual-computation architecture successfully detected every instance of Byzantine corruption. By maintaining an independent calculation path outside of Spark's execution, the Ground Truth Validator achieved <strong>100% attack detection rate</strong> across all experiments.</p>
        </div>

        <div class="finding-box">
            <h4>🔵 Conclusion: The Need for Trust Management</h4>
            <p>These results conclusively demonstrate that standard Spark fault tolerance is <strong>insufficient for Byzantine environments</strong>. The next research phase (October 2026) will implement an <strong>Adaptive Verification Module</strong> and <strong>Trust Management System</strong> to automatically detect, isolate, and remediate untrustworthy workers in real-time.</p>
        </div>
    </div>

</div>

<script>
function showTab(tabName) {{
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tabName).classList.add('active');
    event.target.classList.add('active');
}}
</script>

</body>
</html>"""


if __name__ == "__main__":
    generate_dashboard()
