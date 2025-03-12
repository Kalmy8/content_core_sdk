from functools import lru_cache
from typing import AsyncGenerator

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from content_core_sdk.kafka_client.config import KafkaConfig


class _KafkaService:
    def __init__(self, config: KafkaConfig) -> None:
        self.config = config
        self._producer: AIOKafkaProducer | None = None
        self._consumers: dict[tuple[str, str], AIOKafkaConsumer] = {}

    async def _start_consumer(self, topic: str, group_id: str):
        """
        Lazily initialize and start the Kafka consumer.
        """
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
        )
        self._consumers[(topic, group_id)] = consumer
        await consumer.start()

    async def consume_messages(
        self, topic: str, group_id: str = "default-group"
    ) -> AsyncGenerator[bytes, None]:
        """
        Lazily initialize and consume messages from specified topic/group.
        Usage:
            async for msg in kafka_service.consume_messages("my-topic", "my-group"):
                process(msg)
        """
        consumer_key = (topic, group_id)

        # Initialize consumer
        if consumer_key not in self._consumers:
            await self._start_consumer(topic, group_id)

        consumer = self._consumers[consumer_key]
        try:
            async for msg in consumer:
                yield msg
        except Exception as e:
            await self._stop_consumer(consumer_key)
            raise RuntimeError(f"Consumer error: {e}") from e

    async def _start_producer(self) -> None:
        """
        Lazily initialize and start the Kafka producer.
        """
        if self._producer is None:
            self._producer = AIOKafkaProducer(bootstrap_servers=self.config.bootstrap_servers)
            await self._producer.start()

    async def send_message(self, topic: str, message: bytes) -> None:
        """
        Sends a message to the specified Kafka topic.

        Args:
            topic (str): The Kafka topic to publish to.
            message (str): The message (as a string) to send.
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
