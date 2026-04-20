import os
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/test_online_shop"
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="session")
async def async_client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    async_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    from app.api.dependencies import get_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> dict:
    from app.core.security import hash_password

    user_id = uuid.uuid4()
    user = type("User", (), {})()
    user.id = user_id
    user.email = "testuser@example.com"
    user.username = "testuser"
    user.hashed_password = hash_password("password123")
    user.first_name = "Test"
    user.last_name = "User"
    user.is_active = True
    user.is_superuser = False

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {
        "id": user_id,
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "password123",
    }


@pytest_asyncio.fixture(scope="function")
async def auth_token(async_client: AsyncClient, test_user: dict) -> str:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> dict:
    from app.core.security import hash_password

    user_id = uuid.uuid4()
    user = type("User", (), {})()
    user.id = user_id
    user.email = "admin@example.com"
    user.username = "admin"
    user.hashed_password = hash_password("adminpass123")
    user.first_name = "Admin"
    user.last_name = "User"
    user.is_active = True
    user.is_superuser = True

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {
        "id": user_id,
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpass123",
    }


@pytest_asyncio.fixture(scope="function")
async def admin_token(async_client: AsyncClient, admin_user: dict) -> str:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user["email"],
            "password": admin_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def test_category(db_session: async_sessionmaker, admin_token: str) -> dict:
    from app.models.product import Category

    category_id = uuid.uuid4()
    category = Category(
        id=category_id,
        name="Test Category",
        slug="test-category",
        description="Test category description",
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    return {
        "id": category_id,
        "name": "Test Category",
        "slug": "test-category",
    }


@pytest_asyncio.fixture(scope="function")
async def test_product(db_session: async_sessionmaker, test_category: dict) -> dict:
    from app.models.product import Product
    from decimal import Decimal

    product_id = uuid.uuid4()
    product = Product(
        id=product_id,
        name="Test Product",
        slug="test-product",
        description="Test product description",
        price=Decimal("99.99"),
        stock_quantity=100,
        category_id=test_category["id"],
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    return {
        "id": product_id,
        "name": "Test Product",
        "slug": "test-product",
        "price": 99.99,
    }


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
