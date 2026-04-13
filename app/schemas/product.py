import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    slug: str
    description: str | None = None
    price: float
    old_price: float | None = None
    stock_quantity: int = 0
    category_id: uuid.UUID | None = None
    image_url: str | None = None
    images: list[str] = []

    @field_validator("slug")
    @classmethod
    def slug_must_be_lowercase(cls, v: str) -> str:
        return v.lower().replace(" ", "-")

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def stock_quantity_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock quantity must be non-negative")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: float | None = None
    old_price: float | None = None
    stock_quantity: int | None = None
    category_id: uuid.UUID | None = None
    image_url: str | None = None
    images: list[str] | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    price: float
    old_price: float | None
    stock_quantity: int
    category_id: uuid.UUID | None
    image_url: str | None
    images: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductInListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    price: float
    old_price: float | None
    image_url: str | None


class PaginatedProductsResponse(BaseModel):
    items: list[ProductInListResponse]
    total: int
    page: int
    limit: int
    pages: int


class ProductDetailResponse(ProductResponse):
    category_name: str | None = None


class TrendingProductResponse(BaseModel):
    product_id: uuid.UUID
    slug: str
    name: str
    price: float
    view_count: int
    image_url: str | None
