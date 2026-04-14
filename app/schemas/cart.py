import uuid

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class CartItemAddRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(..., gt=0)

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class CartItemResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    product_slug: str
    quantity: int
    price_at_add: float
    subtotal: float


class CartResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    items: list[CartItemResponse]
    total_amount: float
    items_count: int
