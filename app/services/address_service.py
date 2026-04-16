import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Address
from app.schemas.address import AddressCreate
from app.schemas.address import AddressUpdate


async def get_user_addresses(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Sequence[Address]:
    stmt = select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_address_by_id(
    db: AsyncSession,
    address_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Address | None:
    stmt = select(Address).where(
        Address.id == address_id,
        Address.user_id == user_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_address(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: AddressCreate,
) -> Address:
    if data.is_default:
        await _clear_default_addresses(db, user_id)

    address = Address(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        address_line1=data.address_line1,
        address_line2=data.address_line2,
        city=data.city,
        state=data.state,
        postal_code=data.postal_code,
        country=data.country,
        is_default=data.is_default,
    )
    db.add(address)
    await db.commit()
    await db.refresh(address)

    existing = await get_user_addresses(db, user_id)
    if len(existing) == 1:
        address.is_default = True
        await db.commit()
        await db.refresh(address)

    return address


async def update_address(
    db: AsyncSession,
    address: Address,
    data: AddressUpdate,
) -> Address:
    update_data = data.model_dump(exclude_unset=True)

    if update_data.get("is_default") and not address.is_default:
        await _clear_default_addresses(db, address.user_id)

    for field, value in update_data.items():
        setattr(address, field, value)

    await db.commit()
    await db.refresh(address)
    return address


async def delete_address(
    db: AsyncSession,
    address: Address,
) -> None:
    user_id = address.user_id
    was_default = address.is_default

    await db.delete(address)
    await db.commit()

    if was_default:
        await _set_first_as_default(db, user_id)


async def set_default_address(
    db: AsyncSession,
    address: Address,
) -> Address:
    await _clear_default_addresses(db, address.user_id)
    address.is_default = True
    await db.commit()
    await db.refresh(address)
    return address


async def _clear_default_addresses(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    stmt = (
        update(Address)
        .where(Address.user_id == user_id, Address.is_default)
        .values(is_default=False)
    )
    await db.execute(stmt)
    await db.commit()


async def _set_first_as_default(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    stmt = select(Address).where(Address.user_id == user_id).order_by(Address.created_at).limit(1)
    result = await db.execute(stmt)
    first_address = result.scalar_one_or_none()

    if first_address:
        first_address.is_default = True
        await db.commit()


def address_to_shipping_dict(address: Address) -> dict:
    return {
        "first_name": address.first_name,
        "last_name": address.last_name,
        "phone": address.phone,
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "city": address.city,
        "state": address.state,
        "postal_code": address.postal_code,
        "country": address.country,
    }
