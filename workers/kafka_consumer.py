import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

KAFKA_TOPICS = [
    "user.registered",
    "order.created",
    "order.paid",
    "order.cancelled",
    "product.viewed",
]


async def handle_user_registered(data: dict[str, Any]) -> None:
    from app.services import notification_service

    logger.info(f"Processing user.registered: {data.get('email', 'unknown')}")

    await notification_service.send_welcome_email(
        email=data.get("email", ""),
        username=data.get("username", "User"),
    )


async def handle_order_created(data: dict[str, Any]) -> None:
    from app.services import notification_service

    logger.info(f"Processing order.created: {data.get('order_number', 'unknown')}")

    await notification_service.send_order_confirmation(
        order_number=data.get("order_number", ""),
        email=data.get("email", ""),
        username=data.get("username", "Customer"),
        total_amount=data.get("total_amount", "0"),
        items_count=data.get("items_count", 0),
    )


async def handle_order_paid(data: dict[str, Any]) -> None:
    from app.services import notification_service

    logger.info(f"Processing order.paid: {data.get('order_number', 'unknown')}")

    await notification_service.send_order_paid_notification(
        order_number=data.get("order_number", ""),
        email=data.get("email", ""),
        username=data.get("username", "Customer"),
        total_amount=data.get("total_amount", "0"),
    )


async def handle_order_cancelled(data: dict[str, Any]) -> None:
    from app.services import notification_service

    logger.info(f"Processing order.cancelled: {data.get('order_number', 'unknown')}")

    await notification_service.send_order_cancelled_notification(
        order_number=data.get("order_number", ""),
        email=data.get("email", ""),
        username=data.get("username", "Customer"),
        reason=data.get("reason"),
    )


async def handle_product_viewed(data: dict[str, Any]) -> None:
    from app.services import analytics_service

    logger.info(f"Processing product.viewed: {data.get('product_id', 'unknown')}")

    await analytics_service.handle_product_viewed_event(data)


EVENT_HANDLERS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "user.registered": handle_user_registered,
    "order.created": handle_order_created,
    "order.paid": handle_order_paid,
    "order.cancelled": handle_order_cancelled,
    "product.viewed": handle_product_viewed,
}


class KafkaEventConsumer:
    def __init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *KAFKA_TOPICS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="online-shop-consumer",
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await self._consumer.start()
        self._running = True
        logger.info(f"Kafka consumer started, subscribed to: {KAFKA_TOPICS}")

    async def stop(self) -> None:
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer stopped")

    async def consume(self) -> None:
        if not self._consumer:
            raise RuntimeError("Consumer not started")

        try:
            async for message in self._consumer:
                if not self._running:
                    break

                topic = message.topic
                data = message.value

                logger.info(f"Received event: {topic} -> {data}")

                handler = EVENT_HANDLERS.get(topic)
                if handler:
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"Error handling {topic}: {e}", exc_info=True)
                else:
                    logger.warning(f"No handler for topic: {topic}")

        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
            raise


async def start_consumer() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    from app.core.redis import redis_client

    await redis_client.connect()
    logger.info("Redis connected")

    consumer = KafkaEventConsumer()
    max_retries = 30
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            await consumer.start()
            break
        except KafkaConnectionError as e:
            logger.warning(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Exiting.")
                return

    try:
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        await consumer.stop()
        await redis_client.disconnect()
