import json
from typing import Any

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class RedisClient:
    def __init__(self) -> None:
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        self._client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client not connected")
        return self._client

    async def get(self, key: str) -> Any:
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        await self.client.set(key, json.dumps(value), ex=ex)

    async def delete(self, *keys: str) -> int:
        if keys:
            result: int = await self.client.delete(*keys)
            return result
        return 0

    async def exists(self, key: str) -> bool:
        result: int = await self.client.exists(key)
        return result > 0

    async def incr(self, key: str) -> int:
        result: int = await self.client.incr(key)
        return result

    async def expire(self, key: str, seconds: int) -> bool:
        result: bool = await self.client.expire(key, seconds)
        return result


redis_client = RedisClient()
