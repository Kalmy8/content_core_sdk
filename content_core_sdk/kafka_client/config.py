from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaConfig(BaseSettings):
    """
    Configuration for connecting to a Kafka cluster.
    Provides common configuration parameters for both producers and consumers.
    """
    # Connection settings
    bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    
    # Security settings
    security_protocol: str = Field("PLAINTEXT", env="KAFKA_SECURITY_PROTOCOL")
    sasl_mechanism: Optional[str] = Field(None, env="KAFKA_SASL_MECHANISM")
    sasl_username: Optional[str] = Field(None, env="KAFKA_USERNAME")
    sasl_password: Optional[str] = Field(None, env="KAFKA_PASSWORD")
    
    # Consumer settings
    consumer_auto_offset_reset: str = Field("earliest", env="KAFKA_CONSUMER_AUTO_OFFSET_RESET")
    consumer_enable_auto_commit: bool = Field(True, env="KAFKA_CONSUMER_ENABLE_AUTO_COMMIT")
    consumer_max_poll_records: int = Field(500, env="KAFKA_CONSUMER_MAX_POLL_RECORDS")
    consumer_session_timeout_ms: int = Field(10000, env="KAFKA_CONSUMER_SESSION_TIMEOUT_MS")
    consumer_heartbeat_interval_ms: int = Field(3000, env="KAFKA_CONSUMER_HEARTBEAT_INTERVAL_MS")
    
    # Producer settings
    producer_acks: str = Field("all", env="KAFKA_PRODUCER_ACKS")
    producer_compression_type: Optional[str] = Field(None, env="KAFKA_PRODUCER_COMPRESSION_TYPE")
    producer_max_batch_size: int = Field(16384, env="KAFKA_PRODUCER_MAX_BATCH_SIZE")
    producer_linger_ms: int = Field(0, env="KAFKA_PRODUCER_LINGER_MS")
    producer_enable_idempotence: bool = Field(False, env="KAFKA_PRODUCER_ENABLE_IDEMPOTENCE")
    
    # Advanced settings
    request_timeout_ms: int = Field(40000, env="KAFKA_REQUEST_TIMEOUT_MS")
    retry_backoff_ms: int = Field(100, env="KAFKA_RETRY_BACKOFF_MS")


