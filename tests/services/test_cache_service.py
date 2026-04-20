import uuid
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest


class TestCacheService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_redis = AsyncMock()
        self.mock_redis.get = AsyncMock(return_value=None)
        self.mock_redis.set = AsyncMock(return_value=True)
        self.mock_redis.delete = AsyncMock(return_value=1)
        self.mock_redis.incr = AsyncMock(return_value=1)
        self.mock_redis.expire = AsyncMock(return_value=True)

        self.patcher = patch("app.services.cache_service.redis_client", self.mock_redis)
        self.patcher.start()
        yield
        self.patcher.stop()

    @pytest.mark.asyncio
    async def test_cache_trending_products(self):
        from app.services import cache_service

        products = [{"id": "1", "name": "Product 1"}]
        await cache_service.cache_trending_products(products)

        self.mock_redis.set.assert_called_once()
        call_args = self.mock_redis.set.call_args
        assert call_args[0][0] == "trending:products:v1"
        assert call_args[0][1] == products
        assert call_args[1]["ex"] == 300

    @pytest.mark.asyncio
    async def test_get_cached_trending_products_returns_data(self):
        from app.services import cache_service

        cached_data = [{"id": "1", "name": "Product 1"}]
        self.mock_redis.get.return_value = cached_data

        result = await cache_service.get_cached_trending_products()

        self.mock_redis.get.assert_called_once_with("trending:products:v1")
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_cached_trending_products_returns_none(self):
        from app.services import cache_service

        self.mock_redis.get.return_value = None

        result = await cache_service.get_cached_trending_products()

        assert result is None

    @pytest.mark.asyncio
    async def test_invalidate_trending_cache(self):
        from app.services import cache_service

        await cache_service.invalidate_trending_cache()

        self.mock_redis.delete.assert_called_once_with("trending:products:v1")

    @pytest.mark.asyncio
    async def test_cache_category(self):
        from app.services import cache_service

        category_data = {"id": "123", "name": "Electronics"}
        await cache_service.cache_category("electronics", category_data)

        self.mock_redis.set.assert_called_once_with(
            "category:electronics:v1", category_data, ex=600
        )

    @pytest.mark.asyncio
    async def test_get_cached_category_returns_data(self):
        from app.services import cache_service

        category_data = {"id": "123", "name": "Electronics"}
        self.mock_redis.get.return_value = category_data

        result = await cache_service.get_cached_category("electronics")

        self.mock_redis.get.assert_called_once_with("category:electronics:v1")
        assert result == category_data

    @pytest.mark.asyncio
    async def test_get_cached_category_returns_none(self):
        from app.services import cache_service

        self.mock_redis.get.return_value = None

        result = await cache_service.get_cached_category("electronics")

        assert result is None

    @pytest.mark.asyncio
    async def test_invalidate_category_cache(self):
        from app.services import cache_service

        await cache_service.invalidate_category_cache("electronics")

        self.mock_redis.delete.assert_called_once_with("category:electronics:v1")

    @pytest.mark.asyncio
    async def test_increment_product_views(self):
        from app.services import cache_service

        product_id = uuid.uuid4()
        self.mock_redis.incr.return_value = 1

        count = await cache_service.increment_product_views(product_id)

        expected_key = f"analytics:views:{product_id}"
        self.mock_redis.incr.assert_called_once_with(expected_key)
        self.mock_redis.expire.assert_called_once_with(expected_key, 86400)
        assert count == 1

    @pytest.mark.asyncio
    async def test_increment_product_views_no_expire_on_increment(self):
        from app.services import cache_service

        product_id = uuid.uuid4()
        self.mock_redis.incr.return_value = 5

        count = await cache_service.increment_product_views(product_id)

        self.mock_redis.expire.assert_not_called()
        assert count == 5

    @pytest.mark.asyncio
    async def test_get_product_view_count_returns_value(self):
        from app.services import cache_service

        product_id = uuid.uuid4()
        self.mock_redis.get.return_value = 42

        count = await cache_service.get_product_view_count(product_id)

        expected_key = f"analytics:views:{product_id}"
        self.mock_redis.get.assert_called_once_with(expected_key)
        assert count == 42

    @pytest.mark.asyncio
    async def test_get_product_view_count_returns_zero_for_none(self):
        from app.services import cache_service

        product_id = uuid.uuid4()
        self.mock_redis.get.return_value = None

        count = await cache_service.get_product_view_count(product_id)

        assert count == 0


