import pytest
from producer.event_generator import EventGenerator
from streaming.transformations import process_batch_events
from attacks.controller import AttackController

def test_streaming_transformations_clean():
    gen = EventGenerator(random_seed=42)
    events = gen.generate_batch(100)

    cfg = {"attack": {"enabled": False}}
    controller = AttackController(cfg)

    res = process_batch_events(events, controller)

    assert res["input_count"] == 100
    assert res["processed_count"] == 100
    assert res["dropped_count"] == 0
    assert len(res["sensor_summaries"]) > 0

def test_streaming_transformations_attacked():
    gen = EventGenerator(random_seed=42)
    events = gen.generate_batch(100)

    cfg = {
        "attack": {
            "enabled": True,
            "type": "VALUE_CORRUPTION",
            "probability": 1.0,
            "corruption": {"strategy": "additive", "value": 50.0}
        }
    }
    controller = AttackController(cfg)

    res = process_batch_events(events, controller)

    assert res["input_count"] == 100
    assert res["attacked_count"] > 0
    assert any(s["attack_applied"] for s in res["sensor_summaries"])
