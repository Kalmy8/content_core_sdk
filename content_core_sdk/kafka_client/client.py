from functools import lru_cache
from typing import AsyncGenerator
import logging
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, ConsumerRecord
from content_core_sdk.kafka_client.config import KafkaConfig

logger = logging.getLogger(__name__)

class _KafkaService:
    def __init__(self, config: KafkaConfig) -> None:
        self.config = config
        self._producer: AIOKafkaProducer | None = None
        self._consumers: dict[tuple[str, str], AIOKafkaConsumer] = {}
        logger.info(f"Initialized Kafka service with config: bootstrap_servers={config.bootstrap_servers}, "
                   f"security_protocol={config.security_protocol}, sasl_mechanism={config.sasl_mechanism}, "
                   f"sasl_username={config.sasl_username is not None}")

    async def _start_consumer(self, topic: str, group_id: str) -> None:
        """
        Lazily initialize and start the Kafka consumer.

        Args:
            topic: The Kafka topic to consume
            group_id: The consumer group ID
        """
        consumer_config = {
            "bootstrap_servers": self.config.bootstrap_servers,
            "enable_auto_commit": self.config.consumer_enable_auto_commit,
            "auto_offset_reset": self.config.consumer_auto_offset_reset,
            "max_poll_records": self.config.consumer_max_poll_records,
            "session_timeout_ms": self.config.consumer_session_timeout_ms,
            "heartbeat_interval_ms": self.config.consumer_heartbeat_interval_ms,
            "request_timeout_ms": self.config.request_timeout_ms,
            "retry_backoff_ms": self.config.retry_backoff_ms,
            "security_protocol": self.config.security_protocol
        }

        # Add SASL authentication if required
        if self.config.security_protocol.startswith("SASL"):
            logger.info(f"Adding SASL config with mechanism {self.config.sasl_mechanism}, "
                       f"username={self.config.sasl_username is not None}")
            consumer_config.update({
                "sasl_mechanism": self.config.sasl_mechanism,
                "sasl_plain_username": self.config.sasl_username or "",
                "sasl_plain_password": self.config.sasl_password or "",
            })

        try:
            logger.info(f"Starting consumer for topic {topic} with group {group_id}")
            consumer = AIOKafkaConsumer(topic, group_id=group_id, **consumer_config)
            self._consumers[(topic, group_id)] = consumer
            await consumer.start()
            logger.info(f"Successfully started consumer for topic {topic}")
        except Exception as e:
            logger.error(f"Failed to start consumer: {str(e)}", exc_info=True)
            raise

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
            producer_config = {
                "bootstrap_servers": self.config.bootstrap_servers,
                "acks": self.config.producer_acks,
                "max_batch_size": self.config.producer_max_batch_size,
                "linger_ms": self.config.producer_linger_ms,
                "enable_idempotence": self.config.producer_enable_idempotence,
                "request_timeout_ms": self.config.request_timeout_ms,
                "retry_backoff_ms": self.config.retry_backoff_ms,
                "security_protocol": self.config.security_protocol
            }

            if self.config.producer_compression_type:
                producer_config["compression_type"] = self.config.producer_compression_type

            # Add SASL authentication if required
            if self.config.security_protocol.startswith("SASL"):
                logger.info(f"Adding SASL config to producer with mechanism {self.config.sasl_mechanism}, "
                           f"username={self.config.sasl_username is not None}")
                producer_config.update({
                    "sasl_mechanism": self.config.sasl_mechanism,
                    "sasl_plain_username": self.config.sasl_username or "",
                    "sasl_plain_password": self.config.sasl_password or "",
                })

            try:
                logger.info("Starting Kafka producer")
                self._producer = AIOKafkaProducer(**producer_config)
                await self._producer.start()
                logger.info("Successfully started Kafka producer")
            except Exception as e:
                logger.error(f"Failed to start producer: {str(e)}", exc_info=True)
                raise

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
    config = KafkaConfig()
    return _KafkaService(config=config)