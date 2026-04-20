import pytest
from httpx import AsyncClient


class TestProductList:
    @pytest.mark.asyncio
    async def test_list_products(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    @pytest.mark.asyncio
    async def test_list_products_with_pagination(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/products?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10


class TestProductDetail:
    @pytest.mark.asyncio
    async def test_get_product_by_slug(self, async_client: AsyncClient, test_product: dict):
        response = await async_client.get(f"/api/v1/products/{test_product['slug']}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_product["slug"]

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/products/nonexistent")
        assert response.status_code == 404


class TestProductTrending:
    @pytest.mark.asyncio
    async def test_get_trending(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/products/trending")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestProductCreate:
    @pytest.mark.asyncio
    async def test_create_product_admin(self, async_client: AsyncClient, admin_headers: dict):
        response = await async_client.post(
            "/api/v1/products",
            headers=admin_headers,
            json={
                "name": "New Product",
                "slug": "new-product",
                "description": "New product description",
                "price": 149.99,
                "stock_quantity": 50,
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_product_user_forbidden(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={
                "name": "New Product",
                "slug": "new-product-2",
                "price": 149.99,
                "stock_quantity": 50,
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_product_unauthorized(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/products",
            json={
                "name": "New Product",
                "slug": "new-product-3",
                "price": 149.99,
                "stock_quantity": 50,
            },
        )
        assert response.status_code == 401


class TestProductUpdate:
    @pytest.mark.asyncio
    async def test_update_product_admin(
        self, async_client: AsyncClient, test_product: dict, admin_headers: dict
    ):
        response = await async_client.patch(
            f"/api/v1/products/{test_product['slug']}",
            headers=admin_headers,
            json={"price": 79.99},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_product_user_forbidden(
        self, async_client: AsyncClient, test_product: dict, auth_headers: dict
    ):
        response = await async_client.patch(
            f"/api/v1/products/{test_product['slug']}",
            headers=auth_headers,
            json={"price": 79.99},
        )
        assert response.status_code == 403


class TestProductDelete:
    @pytest.mark.asyncio
    async def test_delete_product_admin(
        self, async_client: AsyncClient, test_product: dict, admin_headers: dict
    ):
        response = await async_client.delete(
            f"/api/v1/products/{test_product['slug']}",
            headers=admin_headers,
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_product_user_forbidden(
        self, async_client: AsyncClient, test_product: dict, auth_headers: dict
    ):
        response = await async_client.delete(
            f"/api/v1/products/{test_product['slug']}",
            headers=auth_headers,
        )
        assert response.status_code == 403
