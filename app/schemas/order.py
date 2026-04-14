import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class ShippingAddress(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str | None = None
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="Russia", max_length=100)


class OrderCreateRequest(BaseModel):
    shipping_address: ShippingAddress
    payment_method: str = Field(default="card", max_length=50)
    notes: str | None = None


class OrderItemResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    product_id: uuid.UUID | None
    product_name: str
    quantity: int
    unit_price: float
    total_price: float


class OrderResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    order_number: str
    status: str
    total_amount: float
    shipping_address: dict
    payment_method: str | None
    payment_status: str
    notes: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
    page: int
    limit: int
    pages: int


class OrderBriefResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    order_number: str
    status: str
    total_amount: float
    items_count: int
    created_at: datetime
