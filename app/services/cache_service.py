import uuid
from typing import Any

from app.core.redis import redis_client

TRENDING_CACHE_KEY = "trending:products:v1"
TRENDING_CACHE_TTL = 300

CATEGORY_CACHE_PREFIX = "category:"
CATEGORY_CACHE_TTL = 600

VIEW_COUNT_PREFIX = "analytics:views:"
VIEW_COUNT_TTL = 86400


async def cache_trending_products(products: list[dict[str, Any]]) -> None:
    await redis_client.set(TRENDING_CACHE_KEY, products, ex=TRENDING_CACHE_TTL)


async def get_cached_trending_products() -> list[dict[str, Any]] | None:
    return await redis_client.get(TRENDING_CACHE_KEY)


async def invalidate_trending_cache() -> None:
    await redis_client.delete(TRENDING_CACHE_KEY)


async def cache_category(slug: str, category_data: dict[str, Any]) -> None:
    key = f"{CATEGORY_CACHE_PREFIX}{slug}:v1"
    await redis_client.set(key, category_data, ex=CATEGORY_CACHE_TTL)


async def get_cached_category(slug: str) -> dict[str, Any] | None:
    key = f"{CATEGORY_CACHE_PREFIX}{slug}:v1"
    return await redis_client.get(key)


async def invalidate_category_cache(slug: str) -> None:
    key = f"{CATEGORY_CACHE_PREFIX}{slug}:v1"
    await redis_client.delete(key)


async def increment_product_views(product_id: str | uuid.UUID) -> int:
    key = f"{VIEW_COUNT_PREFIX}{product_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, VIEW_COUNT_TTL)
    return count


async def get_product_view_count(product_id: str | uuid.UUID) -> int:
    key = f"{VIEW_COUNT_PREFIX}{product_id}"
    count = await redis_client.get(key)
    return count if count else 0
