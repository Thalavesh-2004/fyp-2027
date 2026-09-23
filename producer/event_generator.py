import random
import time
from datetime import datetime, timezone
from typing import Dict, Any, Generator, List

class EventGenerator:
    """Generates synthetic deterministic IoT sensor events."""
    
    def __init__(self, random_seed: int = 42, sensor_count: int = 5,
                 temp_min: float = 15.0, temp_max: float = 45.0,
                 humidity_min: float = 30.0, humidity_max: float = 90.0):
        self.random_seed = random_seed
        self.sensor_count = sensor_count
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.humidity_min = humidity_min
        self.humidity_max = humidity_max
        self.rng = random.Random(random_seed)
        self.sensors = [f"S{i+1:03d}" for i in range(sensor_count)]

    def generate_event(self, event_id: int, base_time: datetime = None) -> Dict[str, Any]:
        """Generate a single deterministic sensor event."""
        if base_time is None:
            base_time = datetime.now(timezone.utc)
        
        sensor_id = self.rng.choice(self.sensors)
        temp = round(self.rng.uniform(self.temp_min, self.temp_max), 2)
        humidity = round(self.rng.uniform(self.humidity_min, self.humidity_max), 2)
        
        return {
            "event_id": event_id,
            "timestamp": base_time.isoformat(),
            "sensor_id": sensor_id,
            "temperature": temp,
            "humidity": humidity
        }

    def generate_stream(self, total_events: int, start_id: int = 1001) -> Generator[Dict[str, Any], None, None]:
        """Generator yielding sequence of sensor events."""
        base_time = datetime.now(timezone.utc)
        for i in range(total_events):
            yield self.generate_event(start_id + i, base_time)

    def generate_batch(self, total_events: int, start_id: int = 1001) -> List[Dict[str, Any]]:
        """Generate a batch list of sensor events."""
        return list(self.generate_stream(total_events, start_id))
