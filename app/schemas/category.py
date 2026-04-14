import uuid
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator


class CategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    slug: str
    description: str | None = None
    parent_id: uuid.UUID | None = None
    image_url: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_must_be_lowercase(cls, v: str) -> str:
        return v.lower().replace(" ", "-")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    slug: str | None = None
    description: str | None = None
    parent_id: uuid.UUID | None = None
    image_url: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    parent_id: uuid.UUID | None
    image_url: str | None
    is_active: bool
    created_at: datetime


class CategoryWithChildrenResponse(CategoryResponse):
    children: list["CategoryResponse"] = []


class CategoryWithProductsResponse(CategoryResponse):
    products: list["ProductSummary"] = []


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    price: float
    image_url: str | None


CategoryWithChildrenResponse.model_rebuild()
CategoryWithProductsResponse.model_rebuild()
