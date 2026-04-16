import uuid
from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class AddressCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str | None = None
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="Russia", max_length=100)
    is_default: bool = Field(default=False)


class AddressUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = None
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=100)


class AddressResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    first_name: str
    last_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str | None
    postal_code: str
    country: str
    is_default: bool
    created_at: datetime


class SetDefaultResponse(BaseModel):
    message: str
    address: AddressResponse
