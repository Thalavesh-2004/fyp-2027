import pytest
from producer.event_generator import EventGenerator

def test_event_generator_reproducibility():
    gen1 = EventGenerator(random_seed=42, sensor_count=3)
    gen2 = EventGenerator(random_seed=42, sensor_count=3)

    events1 = gen1.generate_batch(50)
    events2 = gen2.generate_batch(50)

    assert len(events1) == 50
    assert len(events2) == 50
    for e1, e2 in zip(events1, events2):
        assert e1["sensor_id"] == e2["sensor_id"]
        assert e1["temperature"] == e2["temperature"]
        assert e1["humidity"] == e2["humidity"]

def test_event_schema():
    gen = EventGenerator(random_seed=123)
    event = gen.generate_event(event_id=1001)

    assert "event_id" in event
    assert "timestamp" in event
    assert "sensor_id" in event
    assert "temperature" in event
    assert "humidity" in event
    assert event["event_id"] == 1001
    assert 15.0 <= event["temperature"] <= 45.0
