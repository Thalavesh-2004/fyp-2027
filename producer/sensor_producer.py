import json
import logging
import time
from typing import Dict, Any, Optional, List
from producer.event_generator import EventGenerator

logger = logging.getLogger(__name__)

class SensorProducer:
    """Publishes synthetic sensor events to Kafka topic."""

    def __init__(self, bootstrap_servers: str, topic: str,
                 events_per_second: int = 500, total_events: int = 10000,
                 random_seed: int = 42):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.events_per_second = events_per_second
        self.total_events = total_events
        self.random_seed = random_seed
        self.generator = EventGenerator(random_seed=random_seed)
        self.produced_events: List[Dict[str, Any]] = []

    def publish_all(self, mock: bool = False) -> List[Dict[str, Any]]:
        """Publish events to Kafka (or collect locally if mock mode)."""
        logger.info(f"Starting producer: total={self.total_events}, rate={self.events_per_second}/s, mock={mock}")
        events = self.generator.generate_batch(self.total_events)
        self.produced_events = events

        if mock:
            logger.info(f"[Mock] Produced {len(events)} events locally.")
            return events

        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )

            start_time = time.time()
            sleep_interval = 1.0 / self.events_per_second if self.events_per_second > 0 else 0

            for i, event in enumerate(events):
                producer.send(self.topic, key=event["sensor_id"], value=event)
                if sleep_interval > 0 and (i + 1) % 50 == 0:
                    time.sleep(sleep_interval * 50)

            producer.flush()
            producer.close()
            duration = time.time() - start_time
            rate = len(events) / duration if duration > 0 else 0
            logger.info(f"Successfully published {len(events)} events to '{self.topic}' in {duration:.2f}s ({rate:.1f} ev/s)")
            return events
        except Exception as e:
            logger.error(f"Failed to publish events to Kafka ({self.bootstrap_servers}): {e}")
            logger.info("Falling back to local events buffer for execution.")
            return events
