from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class KafkaConfig(BaseSettings):
    """
    Configuration for connecting to a Kafka cluster.
    Provides common configuration parameters for both producers and consumers.
    """
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        env_file=None,  # No .env file, only use environment variables
        env_nested_delimiter="__",
        extra='ignore',
        case_sensitive=False
    )
    
    # Connection settings
    bootstrap_servers: str
    
    # Security settings
    security_protocol: str = "PLAINTEXT"  # "PLAINTEXT", "SASL_PLAINTEXT", "SSL", "SASL_SSL"
    sasl_mechanism: Optional[str] = None  # "SCRAM-SHA-512", "PLAIN", etc.
    sasl_username: Optional[str] = Field(None, validation_alias="USERNAME")
    sasl_password: Optional[str] = Field(None, validation_alias="PASSWORD")
    
    # Consumer settings
    consumer_auto_offset_reset: str = "earliest"
    consumer_enable_auto_commit: bool = True
    consumer_max_poll_records: int = 500
    consumer_session_timeout_ms: int = 30000
    consumer_heartbeat_interval_ms: int = 10000
    
    # Producer settings
    producer_acks: str = "all"
    producer_compression_type: Optional[str] = None
    producer_max_batch_size: int = 16384
    producer_linger_ms: int = 0
    producer_enable_idempotence: bool = False
    
    # Advanced settings
    request_timeout_ms: int = 40000
    retry_backoff_ms: int = 100
    
