import uuid
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from sqlalchemy import JSON
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


TestBase = declarative_base()


class TestUser(TestBase):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestCategory(TestBase):
    __tablename__ = "categories"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    parent_id = Column(PG_UUID(as_uuid=True), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestProduct(TestBase):
    __tablename__ = "products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    old_price = Column(Numeric(12, 2), nullable=True)
    stock_quantity = Column(Integer, default=0)
    category_id = Column(PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    image_url = Column(String(500), nullable=True)
    images = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestCart(TestBase):
    __tablename__ = "carts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestCartItem(TestBase):
    __tablename__ = "cart_items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(PG_UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, not_null_default=1)
    price_at_add = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.exists = AsyncMock(return_value=False)
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_kafka_producer():
    producer = AsyncMock()
    producer.send = AsyncMock(return_value=MagicMock())
    producer.send_and_wait = AsyncMock()
    return producer


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+79001234567",
    }


@pytest.fixture
def sample_category_data() -> dict[str, Any]:
    return {
        "name": "Electronics",
        "slug": "electronics",
        "description": "Electronic devices and accessories",
    }


@pytest.fixture
def sample_product_data() -> dict[str, Any]:
    return {
        "name": "Test Product",
        "slug": "test-product",
        "description": "A test product description",
        "price": 99.99,
        "old_price": 129.99,
        "stock_quantity": 100,
        "image_url": "https://example.com/product.jpg",
        "images": [],
    }


@pytest.fixture
def sample_cart_item_data() -> dict[str, Any]:
    return {
        "quantity": 2,
    }


@pytest.fixture
def sample_shipping_address() -> dict[str, Any]:
    return {
        "first_name": "Test",
        "last_name": "User",
        "phone": "+79001234567",
        "address_line1": "123 Main St",
        "address_line2": "Apt 4",
        "city": "Moscow",
        "state": "Moscow Oblast",
        "postal_code": "123456",
        "country": "Russia",
    }


@pytest_asyncio.fixture
async def db_user(db_session: AsyncSession, sample_user_data: dict) -> TestUser:
    from app.core.security import hash_password

    user = TestUser(
        id=uuid.uuid4(),
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        hashed_password=hash_password(sample_user_data["password"]),
        first_name=sample_user_data["first_name"],
        last_name=sample_user_data["last_name"],
        phone=sample_user_data["phone"],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def db_category(db_session: AsyncSession, sample_category_data: dict) -> TestCategory:
    category = TestCategory(
        id=uuid.uuid4(),
        name=sample_category_data["name"],
        slug=sample_category_data["slug"],
        description=sample_category_data["description"],
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def db_product(
    db_session: AsyncSession, sample_product_data: dict, db_category: TestCategory
) -> TestProduct:
    from decimal import Decimal

    product = TestProduct(
        id=uuid.uuid4(),
        name=sample_product_data["name"],
        slug=sample_product_data["slug"],
        description=sample_product_data["description"],
        price=Decimal(str(sample_product_data["price"])),
        old_price=Decimal(str(sample_product_data["old_price"]))
        if sample_product_data.get("old_price")
        else None,
        stock_quantity=sample_product_data["stock_quantity"],
        category_id=db_category.id,
        image_url=sample_product_data["image_url"],
        images=sample_product_data["images"],
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def db_cart(db_session: AsyncSession, db_user: TestUser) -> TestCart:
    cart = TestCart(id=uuid.uuid4(), user_id=db_user.id)
    db_session.add(cart)
    await db_session.commit()
    await db_session.refresh(cart)
    return cart
