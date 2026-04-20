import pytest
from httpx import AsyncClient


class TestAuthRegister:
    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient, test_user: dict):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user["email"],
                "username": "different",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, async_client: AsyncClient, test_user: dict):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user["username"],
                "password": "password123",
            },
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 422


class TestAuthLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user: dict):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient, test_user: dict):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401


class TestAuthMe:
    @pytest.mark.asyncio
    async def test_get_me(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@example.com"

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestAuthLogout:
    @pytest.mark.asyncio
    async def test_logout(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestAuthRefresh:
    @pytest.mark.asyncio
    async def test_refresh_token(self, async_client: AsyncClient, test_user: dict):
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code == 401
