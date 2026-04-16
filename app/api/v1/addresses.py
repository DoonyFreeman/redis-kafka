import uuid
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.address import AddressCreate
from app.schemas.address import AddressResponse
from app.schemas.address import AddressUpdate
from app.schemas.address import SetDefaultResponse
from app.services import address_service

router = APIRouter(prefix="/addresses", tags=["addresses"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_active_user)]


@router.get("", response_model=list[AddressResponse])
async def list_addresses(
    db: DbDep,
    user: UserDep,
) -> list[AddressResponse]:
    addresses = await address_service.get_user_addresses(db, user.id)
    return [AddressResponse.model_validate(addr) for addr in addresses]


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    data: AddressCreate,
    db: DbDep,
    user: UserDep,
) -> AddressResponse:
    address = await address_service.create_address(db, user.id, data)
    return AddressResponse.model_validate(address)


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: uuid.UUID,
    db: DbDep,
    user: UserDep,
) -> AddressResponse:
    address = await address_service.get_address_by_id(db, address_id, user.id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    return AddressResponse.model_validate(address)


@router.patch("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: uuid.UUID,
    data: AddressUpdate,
    db: DbDep,
    user: UserDep,
) -> AddressResponse:
    address = await address_service.get_address_by_id(db, address_id, user.id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    updated = await address_service.update_address(db, address, data)
    return AddressResponse.model_validate(updated)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: uuid.UUID,
    db: DbDep,
    user: UserDep,
) -> None:
    address = await address_service.get_address_by_id(db, address_id, user.id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    await address_service.delete_address(db, address)


@router.post("/{address_id}/default", response_model=SetDefaultResponse)
async def set_default_address(
    address_id: uuid.UUID,
    db: DbDep,
    user: UserDep,
) -> SetDefaultResponse:
    address = await address_service.get_address_by_id(db, address_id, user.id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    updated = await address_service.set_default_address(db, address)
    return SetDefaultResponse(
        message="Address set as default",
        address=AddressResponse.model_validate(updated),
    )
