CREATE TABLE IF NOT EXISTS experiments (
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

CREATE TABLE IF NOT EXISTS execution_records (
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

CREATE TABLE IF NOT EXISTS validation_results (
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

CREATE TABLE IF NOT EXISTS attack_events (
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

CREATE TABLE IF NOT EXISTS experiment_summary (
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
