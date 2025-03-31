from functools import lru_cache
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, ConsumerRecord
from content_core_sdk.kafka_client.config import KafkaConfig
from content_core_sdk.common.result import Result

class _KafkaService:
    def __init__(self, config: KafkaConfig) -> None:
        self.config = config
        self._producer: AIOKafkaProducer | None = None
        self._consumers: dict[tuple[str, str], AIOKafkaConsumer] = {}

    def _create_consumer_config(self) -> Result[dict]:
        """
        Creates a configuration dictionary for the Kafka consumer based on the settings from KafkaConfig.
        
        Returns:
            Result containing either the consumer configuration dictionary or an error
        """
        try:
            consumer_config = {
                "bootstrap_servers": self.config.bootstrap_servers,
                "auto_offset_reset": self.config.consumer_auto_offset_reset,
                "enable_auto_commit": self.config.consumer_enable_auto_commit,
                "max_poll_records": self.config.consumer_max_poll_records,
                "session_timeout_ms": self.config.consumer_session_timeout_ms,
                "heartbeat_interval_ms": self.config.consumer_heartbeat_interval_ms,
                "request_timeout_ms": self.config.request_timeout_ms,
                "retry_backoff_ms": self.config.retry_backoff_ms,
                "security_protocol": self.config.security_protocol
            }

            if self.config.security_protocol.startswith("SASL"):
                consumer_config.update({
                    "sasl_mechanism": self.config.sasl_mechanism,
                    "sasl_plain_username": self.config.sasl_username or "",
                    "sasl_plain_password": self.config.sasl_password or "",
                })

            return Result.success(consumer_config)
        except Exception as e:
            return Result.error(f"Failed to create consumer config: {str(e)}", e)

    async def _start_consumer(self, topic: str, group_id: str) -> Result[None]:
        """
        Lazily initialize and start the Kafka consumer.

        Args:
            topic: The Kafka topic to consume
            group_id: The consumer group ID
        """
        config_result = self._create_consumer_config()
        if config_result.is_error:
            return config_result
        consumer_config = config_result.value

        try:
            consumer = AIOKafkaConsumer(topic, group_id=group_id, **consumer_config)
            self._consumers[(topic, group_id)] = consumer
            await consumer.start()
            return Result.success(None)
        except Exception as e:
            return Result.error(f"Failed to start consumer: {str(e)}", e)

    async def consume_messages(
        self, topic: str, group_id: str = "default-group"
    ) -> Result[AsyncGenerator[ConsumerRecord, None]]:
        """
        Lazily initialize and consume messages from specified topic/group.
        
        Args:
            topic: The Kafka topic to consume
            group_id: The consumer group ID
        """
        consumer_key = (topic, group_id)

        if consumer_key not in self._consumers:
            result = await self._start_consumer(topic, group_id)
            if result.is_error:
                return result

        consumer = self._consumers[consumer_key]
        try:
            async def message_generator():
                try:
                    async for msg in consumer:
                        yield msg
                except Exception as e:
                    await self._stop_consumer(consumer_key)
                    raise RuntimeError(f"Consumer error: {e}") from e

            return Result.success(message_generator())
        except Exception as e:
            return Result.error(f"Failed to create message generator: {str(e)}", e)
    
    def _create_producer_config(self) -> Result[dict]:
        """
        Creates a configuration dictionary for the Kafka producer based on the settings from KafkaConfig.
        
        Returns:
            Result containing either the producer configuration dictionary or an error
        """
        try:
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

            if self.config.security_protocol.startswith("SASL"):
                producer_config.update({
                    "sasl_mechanism": self.config.sasl_mechanism,
                    "sasl_plain_username": self.config.sasl_username or "",
                    "sasl_plain_password": self.config.sasl_password or "",
                })

            return Result.success(producer_config)
        except Exception as e:
            return Result.error(f"Failed to create producer config: {str(e)}", e)

    async def _start_producer(self) -> Result[None]:
        """
        Lazily initialize and start the Kafka producer.
        """
        if self._producer is None:
            config_result = self._create_producer_config()
            if config_result.is_error:
                return config_result
            producer_config = config_result.value

            try:
                self._producer = AIOKafkaProducer(**producer_config)
                await self._producer.start()
                return Result.success(None)
            except Exception as e:
                return Result.error(f"Failed to start producer: {str(e)}", e)

    async def send_message(self, topic: str, message: bytes) -> Result[None]:
        """
        Sends a message to the specified Kafka topic.

        Args:
            topic: The Kafka topic to publish to
            message: The message (as bytes) to send
        """
        if self._producer is None:
            result = await self._start_producer()
            if result.is_error:
                return result

        try:
            await self._producer.send_and_wait(topic, message)
            return Result.success(None)
        except Exception as e:
            return Result.error(f"Failed to send message: {str(e)}", e)

    async def _stop_producer(self) -> Result[None]:
        """
        Stops the Kafka producer gracefully.
        """
        if self._producer is not None:
            try:
                await self._producer.stop()
                self._producer = None
                return Result.success(None)
            except Exception as e:
                return Result.error(f"Failed to stop producer: {str(e)}", e)

    async def _stop_consumer(self, consumer_key: tuple[str, str]) -> Result[None]:
        """Stop and remove a specific consumer"""
        if consumer := self._consumers.pop(consumer_key, None):
            try:
                await consumer.stop()
                return Result.success(None)
            except Exception as e:
                return Result.error(f"Failed to stop consumer: {str(e)}", e)

    async def _stop_all_consumers(self) -> Result[None]:
        """Gracefully stop all active consumers"""
        for consumer_key in list(self._consumers.keys()):
            result = await self._stop_consumer(consumer_key)
            if result.is_error:
                return result
        return Result.success(None)

    async def close(self) -> Result[None]:
        """Cleanup all resources"""
        consumers_result = await self._stop_all_consumers()
        if consumers_result.is_error:
            return consumers_result
        
        producer_result = await self._stop_producer()
        if producer_result.is_error:
            return producer_result
            
        return Result.success(None)


@lru_cache(maxsize=1)
def get_kafka_service() -> Result[_KafkaService]:
    """
    Returns a Result containing either a singleton instance of _KafkaService or an error.
    """
    try:
        config = KafkaConfig()
        return Result.success(_KafkaService(config=config))
    except Exception as e:
        return Result.error(f"Failed to initialize Kafka service: {str(e)}", e)