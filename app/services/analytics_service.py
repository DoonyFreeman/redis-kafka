import logging
from typing import Any

from app.config import get_settings
from app.core.redis import redis_client
from app.services import cache_service

settings = get_settings()
logger = logging.getLogger(__name__)

TRENDING_PRODUCT_LIMIT = 20
VIEW_COUNT_PATTERN = "analytics:views:*"


async def update_trending_from_views() -> list[dict[str, Any]]:
    view_counts: dict[str, int] = {}

    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(
            cursor=cursor,
            match=VIEW_COUNT_PATTERN,
            count=100,
        )
        for key in keys:
            product_id = key.replace("analytics:views:", "")
            count = await redis_client.get(key)
            if count:
                view_counts[product_id] = int(count)

        if cursor == 0:
            break

    if not view_counts:
        logger.info("No product views found for trending")
        return []

    sorted_products = sorted(
        view_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:TRENDING_PRODUCT_LIMIT]

    trending_list = [
        {"product_id": product_id, "view_count": count} for product_id, count in sorted_products
    ]

    await cache_service.cache_trending_products(trending_list)

    logger.info(f"Updated trending products: {len(trending_list)} items")
    return trending_list


async def handle_product_viewed_event(event: dict[str, Any]) -> None:
    product_id = event.get("product_id")
    if not product_id:
        logger.warning("product.viewed event missing product_id")
        return

    logger.info(f"Processing product.viewed for {product_id}")

    await cache_service.increment_product_views(product_id)

    await update_trending_from_views()
