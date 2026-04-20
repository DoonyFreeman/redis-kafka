import pytest
from httpx import AsyncClient


class TestOrderList:
    @pytest.mark.asyncio
    async def test_list_orders(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get(
            "/api/v1/orders",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_orders_unauthorized(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/orders")
        assert response.status_code == 401


class TestOrderCreate:
    @pytest.mark.asyncio
    async def test_create_order(
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
                "quantity": 2,
            },
        )

        response = await async_client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                    "country": "Russia",
                },
                "payment_method": "card",
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_order_empty_cart(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                    "country": "Russia",
                },
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_order_unauthorized(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                },
            },
        )
        assert response.status_code == 401


class TestOrderDetail:
    @pytest.mark.asyncio
    async def test_get_order_by_number(
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

        create_response = await async_client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                    "country": "Russia",
                },
            },
        )
        order_number = create_response.json()["order_number"]

        response = await async_client.get(
            f"/api/v1/orders/{order_number}",
            headers=auth_headers,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_order_not_found(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get(
            "/api/v1/orders/ORD-999-XXXXX",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestOrderCancel:
    @pytest.mark.asyncio
    async def test_cancel_order_pending(
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

        create_response = await async_client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                    "country": "Russia",
                },
            },
        )
        order_number = create_response.json()["order_number"]

        response = await async_client.patch(
            f"/api/v1/orders/{order_number}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_order_paid(
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

        create_response = await async_client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                    "country": "Russia",
                },
            },
        )
        order_number = create_response.json()["order_number"]

        await async_client.post(
            f"/api/v1/orders/{order_number}/pay",
            headers=auth_headers,
        )

        response = await async_client.patch(
            f"/api/v1/orders/{order_number}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestOrderPay:
    @pytest.mark.asyncio
    async def test_pay_order(
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

        create_response = await async_client.post(
            "/api/v1/orders",
            headers=auth_headers,
            json={
                "shipping_address": {
                    "first_name": "Test",
                    "last_name": "User",
                    "phone": "+79001234567",
                    "address_line1": "123 Main St",
                    "city": "Moscow",
                    "postal_code": "123456",
                    "country": "Russia",
                },
            },
        )
        order_number = create_response.json()["order_number"]

        response = await async_client.post(
            f"/api/v1/orders/{order_number}/pay",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["payment_status"] == "paid"
