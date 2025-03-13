import os
from dataclasses import dataclass
from typing import Self, Optional


@dataclass
class KafkaConfig:
    """
    Configuration for connecting to a Kafka cluster.
    Provides common configuration parameters for both producers and consumers.
    """
    # Connection settings
    bootstrap_servers: str
    
    # Consumer settings
    consumer_auto_offset_reset: str = "earliest"  # 'earliest', 'latest', or 'none'
    consumer_enable_auto_commit: bool = True
    consumer_max_poll_records: int = 500
    consumer_session_timeout_ms: int = 10000
    consumer_heartbeat_interval_ms: int = 3000
    
    # Producer settings
    producer_acks: str = "all"  # '0', '1', or 'all'
    producer_compression_type: Optional[str] = None  # 'gzip', 'snappy', 'lz4', or None
    producer_max_batch_size: int = 16384
    producer_linger_ms: int = 0
    producer_enable_idempotence: bool = False
    
    # Advanced settings
    request_timeout_ms: int = 40000
    retry_backoff_ms: int = 100

    @classmethod
    def from_env(cls) -> Self:
        """
        Create a KafkaConfig from environment variables.
        
        Environment variables:
        - KAFKA_BOOTSTRAP_SERVERS: Required
        - KAFKA_CONSUMER_AUTO_OFFSET_RESET: Optional, default 'earliest'
        - KAFKA_CONSUMER_ENABLE_AUTO_COMMIT: Optional, default 'true'
        - KAFKA_CONSUMER_MAX_POLL_RECORDS: Optional, default 500
        - KAFKA_CONSUMER_SESSION_TIMEOUT_MS: Optional, default 10000
        - KAFKA_CONSUMER_HEARTBEAT_INTERVAL_MS: Optional, default 3000
        - KAFKA_PRODUCER_ACKS: Optional, default 'all'
        - KAFKA_PRODUCER_COMPRESSION_TYPE: Optional, default None
        - KAFKA_PRODUCER_MAX_BATCH_SIZE: Optional, default 16384
        - KAFKA_PRODUCER_LINGER_MS: Optional, default 0
        - KAFKA_PRODUCER_ENABLE_IDEMPOTENCE: Optional, default 'false'
        - KAFKA_REQUEST_TIMEOUT_MS: Optional, default 40000
        - KAFKA_RETRY_BACKOFF_MS: Optional, default 100
        """
        # Parse boolean values
        def parse_bool(env_var, default):
            value = os.getenv(env_var)
            if value is None:
                return default
            return value.lower() in ('true', 'yes', '1', 't', 'y')
            
        # Parse int values
        def parse_int(env_var, default):
            value = os.getenv(env_var)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default
                
        # Parse string values with None handling
        def parse_str(env_var, default):
            value = os.getenv(env_var)
            if value is None or value.lower() in ('none', 'null'):
                return default
            return value

        # Check required environment variables
        bootstrap_servers = parse_str("KAFKA_BOOTSTRAP_SERVERS", None)
        if not bootstrap_servers:
            raise EnvironmentError("Missing required environment variable: KAFKA_BOOTSTRAP_SERVERS")
            
        return cls(
            # Connection settings
            bootstrap_servers=bootstrap_servers,
            
            # Consumer settings
            consumer_auto_offset_reset=parse_str("KAFKA_CONSUMER_AUTO_OFFSET_RESET", "earliest"),
            consumer_enable_auto_commit=parse_bool("KAFKA_CONSUMER_ENABLE_AUTO_COMMIT", True),
            consumer_max_poll_records=parse_int("KAFKA_CONSUMER_MAX_POLL_RECORDS", 500),
            consumer_session_timeout_ms=parse_int("KAFKA_CONSUMER_SESSION_TIMEOUT_MS", 10000),
            consumer_heartbeat_interval_ms=parse_int("KAFKA_CONSUMER_HEARTBEAT_INTERVAL_MS", 3000),
            
            # Producer settings
            producer_acks=parse_str("KAFKA_PRODUCER_ACKS", "all"),
            producer_compression_type=parse_str("KAFKA_PRODUCER_COMPRESSION_TYPE", None),
            producer_max_batch_size=parse_int("KAFKA_PRODUCER_MAX_BATCH_SIZE", 16384),
            producer_linger_ms=parse_int("KAFKA_PRODUCER_LINGER_MS", 0),
            producer_enable_idempotence=parse_bool("KAFKA_PRODUCER_ENABLE_IDEMPOTENCE", False),
            
            # Advanced settings
            request_timeout_ms=parse_int("KAFKA_REQUEST_TIMEOUT_MS", 40000),
            retry_backoff_ms=parse_int("KAFKA_RETRY_BACKOFF_MS", 100)
        )

