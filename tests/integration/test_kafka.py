import pytest
from producer.sensor_producer import SensorProducer
from producer.event_generator import EventGenerator

def test_producer_mock_generation():
    producer = SensorProducer(
        bootstrap_servers="localhost:29092",
        topic="test-topic",
        events_per_second=1000,
        total_events=500,
        random_seed=42
    )
    events = producer.publish_all(mock=True)

    assert len(events) == 500
    assert events[0]["event_id"] == 1001
    assert events[-1]["event_id"] == 1500
