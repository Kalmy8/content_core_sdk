from functools import lru_cache
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, ConsumerRecord
from content_core_sdk.kafka_client.config import KafkaConfig


class _KafkaService:
    def __init__(self, config: KafkaConfig) -> None:
        self.config = config
        self._producer: AIOKafkaProducer | None = None
        self._consumers: dict[tuple[str, str], AIOKafkaConsumer] = {}

    async def _start_consumer(self, topic: str, group_id: str) -> None:
        """
        Lazily initialize and start the Kafka consumer.
        
        Args:
            topic: The Kafka topic to consume
            group_id: The consumer group ID
        """
        # Use configuration directly from KafkaConfig
        consumer = AIOKafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=self.config.bootstrap_servers,
            enable_auto_commit=self.config.consumer_enable_auto_commit,
            auto_offset_reset=self.config.consumer_auto_offset_reset,
            max_poll_records=self.config.consumer_max_poll_records,
            session_timeout_ms=self.config.consumer_session_timeout_ms,
            heartbeat_interval_ms=self.config.consumer_heartbeat_interval_ms,
            request_timeout_ms=self.config.request_timeout_ms,
            retry_backoff_ms=self.config.retry_backoff_ms
        )
        self._consumers[(topic, group_id)] = consumer
        await consumer.start()

    async def consume_messages(
        self, topic: str, group_id: str = "default-group"
    ) -> AsyncGenerator[ConsumerRecord, None]:
        """
        Lazily initialize and consume messages from specified topic/group.
        
        Args:
            topic: The Kafka topic to consume
            group_id: The consumer group ID
        """
        consumer_key = (topic, group_id)

        if consumer_key not in self._consumers:
            await self._start_consumer(topic, group_id)

        consumer = self._consumers[consumer_key]
        try:
            async for msg in consumer:
                yield msg
        except Exception as e:
            await self._stop_consumer(consumer_key)
            raise RuntimeError(f"Consumer error: {e}") from e

    async def _start_producer(self):
        """
        Lazily initialize and start the Kafka producer.
        """
        if self._producer is None:
            # Build producer configuration from KafkaConfig
            producer_config = {
                "bootstrap_servers": self.config.bootstrap_servers,
                "acks": self.config.producer_acks,
                "max_batch_size": self.config.producer_max_batch_size,
                "linger_ms": self.config.producer_linger_ms,
                "enable_idempotence": self.config.producer_enable_idempotence,
                "request_timeout_ms": self.config.request_timeout_ms,
                "retry_backoff_ms": self.config.retry_backoff_ms
            }
            
            # Only add compression if it's specified (not None)
            if self.config.producer_compression_type:
                producer_config["compression_type"] = self.config.producer_compression_type
            
            # Create and start producer
            self._producer = AIOKafkaProducer(**producer_config)
            await self._producer.start()

    async def send_message(self, topic: str, message: bytes) -> None:
        """
        Sends a message to the specified Kafka topic.

        Args:
            topic: The Kafka topic to publish to
            message: The message (as bytes) to send
        """
        if self._producer is None:
            await self._start_producer()
        await self._producer.send_and_wait(topic, message)

    async def _stop_producer(self) -> None:
        """
        Stops the Kafka producer gracefully.
        """
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def _stop_consumer(self, consumer_key: tuple[str, str]) -> None:
        """Stop and remove a specific consumer"""
        if consumer := self._consumers.pop(consumer_key, None):
            await consumer.stop()

    async def _stop_all_consumers(self) -> None:
        """Gracefully stop all active consumers"""
        for consumer_key in list(self._consumers.keys()):
            await self._stop_consumer(consumer_key)

    async def close(self) -> None:
        """Cleanup all resources"""
        await self._stop_all_consumers()
        await self._stop_producer()


@lru_cache(maxsize=1)
def get_kafka_service() -> _KafkaService:
    """
    Returns a singleton instance of _KafkaService.
    """
    config = KafkaConfig.from_env()
    return _KafkaService(config=config)
