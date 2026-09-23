from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType, TimestampType

def get_sensor_event_schema() -> StructType:
    """Returns PySpark schema for synthetic IoT sensor events."""
    return StructType([
        StructField("event_id", LongType(), False),
        StructField("timestamp", StringType(), False),
        StructField("sensor_id", StringType(), False),
        StructField("temperature", DoubleType(), False),
        StructField("humidity", DoubleType(), False)
    ])
