import logging
import time
from typing import List, Optional

logger = logging.getLogger(__name__)

def check_kafka_connection(bootstrap_servers: str, timeout_sec: int = 10) -> bool:
    """Check if Kafka cluster is reachable."""
    try:
        from kafka import KafkaAdminClient
        admin = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            request_timeout_ms=timeout_sec * 1000
        )
        cluster_info = admin.describe_cluster()
        admin.close()
        logger.info(f"Successfully connected to Kafka cluster at {bootstrap_servers}: {cluster_info}")
        return True
    except Exception as e:
        logger.warning(f"Could not connect to Kafka at {bootstrap_servers}: {e}")
        return False

def create_topic_if_not_exists(bootstrap_servers: str, topic_name: str,
                                num_partitions: int = 3, replication_factor: int = 1) -> bool:
    """Ensure topic exists on Kafka broker."""
    try:
        from kafka.admin import KafkaAdminClient, NewTopic
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        existing_topics = admin.list_topics()
        if topic_name not in existing_topics:
            topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
            admin.create_topics(new_topics=[topic], validate_only=False)
            logger.info(f"Created Kafka topic: {topic_name} with {num_partitions} partitions")
        else:
            logger.info(f"Kafka topic '{topic_name}' already exists.")
        admin.close()
        return True
    except Exception as e:
        logger.error(f"Failed to create or verify topic {topic_name}: {e}")
        return False
