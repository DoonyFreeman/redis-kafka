import json
from typing import Any

from aiokafka import AIOKafkaProducer

from app.config import get_settings

settings = get_settings()


class KafkaProducer:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def send(self, topic: str, value: dict[str, Any]) -> None:
        if self._producer is None:
            raise RuntimeError("Kafka producer not started")
        await self._producer.send_and_wait(topic, value)


kafka_producer = KafkaProducer()
