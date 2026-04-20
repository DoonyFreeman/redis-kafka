import pytest
from httpx import AsyncClient


class TestCartGet:
    @pytest.mark.asyncio
    async def test_get_empty_cart(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get(
            "/api/v1/cart",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_amount" in data

    @pytest.mark.asyncio
    async def test_get_cart_unauthorized(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/cart")
        assert response.status_code == 401


class TestCartAddItem:
    @pytest.mark.asyncio
    async def test_add_item_to_cart(
        self, async_client: AsyncClient, auth_headers: dict, test_product: dict
    ):
        response = await async_client.post(
            "/api/v1/cart/items",
            headers=auth_headers,
            json={
                "product_id": str(test_product["id"]),
                "quantity": 2,
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_add_item_product_not_found(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.post(
            "/api/v1/cart/items",
            headers=auth_headers,
            json={
                "product_id": "00000000-0000-0000-0000-000000000000",
                "quantity": 1,
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_item_unauthorized(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/cart/items",
            json={
                "product_id": "00000000-0000-0000-0000-000000000000",
                "quantity": 1,
            },
        )
        assert response.status_code == 401


class TestCartUpdateItem:
    @pytest.mark.asyncio
    async def test_update_item_quantity(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_product: dict,
    ):
        add_response = await async_client.post(
            "/api/v1/cart/items",
            headers=auth_headers,
            json={
                "product_id": str(test_product["id"]),
                "quantity": 1,
            },
        )
        item_id = add_response.json()["id"]

        response = await async_client.patch(
            f"/api/v1/cart/items/{item_id}",
            headers=auth_headers,
            json={"quantity": 5},
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 5

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.patch(
            "/api/v1/cart/items/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
            json={"quantity": 5},
        )
        assert response.status_code == 404


class TestCartRemoveItem:
    @pytest.mark.asyncio
    async def test_remove_item(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_product: dict,
    ):
        add_response = await async_client.post(
            "/api/v1/cart/items",
            headers=auth_headers,
            json={
                "product_id": str(test_product["id"]),
                "quantity": 1,
            },
        )
        item_id = add_response.json()["id"]

        response = await async_client.delete(
            f"/api/v1/cart/items/{item_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204


class TestCartClear:
    @pytest.mark.asyncio
    async def test_clear_cart(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_product: dict,
    ):
        await async_client.post(
            "/api/v1/cart/items",
            headers=auth_headers,
            json={
                "product_id": str(test_product["id"]),
                "quantity": 1,
            },
        )

        response = await async_client.delete(
            "/api/v1/cart",
            headers=auth_headers,
        )
        assert response.status_code == 204
