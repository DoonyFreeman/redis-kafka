import pytest
from httpx import AsyncClient


class TestCategoryList:
    @pytest.mark.asyncio
    async def test_list_categories(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCategoryDetail:
    @pytest.mark.asyncio
    async def test_get_category_by_slug(self, async_client: AsyncClient, test_category: dict):
        response = await async_client.get(f"/api/v1/categories/{test_category['slug']}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_category["slug"]

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/categories/nonexistent")
        assert response.status_code == 404


class TestCategoryCreate:
    @pytest.mark.asyncio
    async def test_create_category_admin(self, async_client: AsyncClient, admin_headers: dict):
        response = await async_client.post(
            "/api/v1/categories",
            headers=admin_headers,
            json={
                "name": "New Category",
                "slug": "new-category",
                "description": "New category description",
            },
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_category_user_forbidden(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.post(
            "/api/v1/categories",
            headers=auth_headers,
            json={
                "name": "New Category",
                "slug": "new-category-2",
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_category_unauthorized(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/categories",
            json={
                "name": "New Category",
                "slug": "new-category-3",
            },
        )
        assert response.status_code == 401


class TestCategoryUpdate:
    @pytest.mark.asyncio
    async def test_update_category_admin(
        self, async_client: AsyncClient, test_category: dict, admin_headers: dict
    ):
        response = await async_client.patch(
            f"/api/v1/categories/{test_category['slug']}",
            headers=admin_headers,
            json={"name": "Updated Category"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_category_user_forbidden(
        self, async_client: AsyncClient, test_category: dict, auth_headers: dict
    ):
        response = await async_client.patch(
            f"/api/v1/categories/{test_category['slug']}",
            headers=auth_headers,
            json={"name": "Updated Category"},
        )
        assert response.status_code == 403


class TestCategoryDelete:
    @pytest.mark.asyncio
    async def test_delete_category_admin(
        self, async_client: AsyncClient, test_category: dict, admin_headers: dict
    ):
        response = await async_client.delete(
            f"/api/v1/categories/{test_category['slug']}",
            headers=admin_headers,
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_category_user_forbidden(
        self, async_client: AsyncClient, test_category: dict, auth_headers: dict
    ):
        response = await async_client.delete(
            f"/api/v1/categories/{test_category['slug']}",
            headers=auth_headers,
        )
        assert response.status_code == 403
