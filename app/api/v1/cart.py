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
from app.schemas.cart import CartItemAddRequest
from app.schemas.cart import CartItemResponse
from app.schemas.cart import CartItemUpdateRequest
from app.schemas.cart import CartResponse
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_active_user)]


@router.get("", response_model=CartResponse)
async def get_cart(
    db: DbDep,
    user: UserDep,
) -> CartResponse:
    cart = await cart_service.get_or_create_cart(db, user.id)
    _, items, total = await cart_service.get_cart_with_items(db, cart.id)

    cart_items = []
    for item in items:
        product_stmt = await cart_service.get_product_by_id(db, item.product_id)
        product_name = product_stmt.name if product_stmt else "Unknown"
        product_slug = product_stmt.slug if product_stmt else ""

        cart_items.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product_name,
                product_slug=product_slug,
                quantity=item.quantity,
                price_at_add=float(item.price_at_add),
                subtotal=float(item.price_at_add) * item.quantity,
            )
        )

    return CartResponse(
        id=cart.id,
        items=cart_items,
        total_amount=total,
        items_count=len(cart_items),
    )


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    data: CartItemAddRequest,
    db: DbDep,
    user: UserDep,
) -> CartItemResponse:
    cart = await cart_service.get_or_create_cart(db, user.id)

    try:
        item = await cart_service.add_item(db, cart.id, data.product_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    product = await cart_service.get_product_by_id(db, item.product_id)
    product_name = product.name if product else "Unknown"
    product_slug = product.slug if product else ""

    return CartItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=product_name,
        product_slug=product_slug,
        quantity=item.quantity,
        price_at_add=float(item.price_at_add),
        subtotal=float(item.price_at_add) * item.quantity,
    )


@router.patch("/items/{item_id}", response_model=CartItemResponse)
async def update_item(
    item_id: uuid.UUID,
    data: CartItemUpdateRequest,
    db: DbDep,
    user: UserDep,
) -> CartItemResponse:
    item = await cart_service.get_cart_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id '{item_id}' not found",
        )

    cart = await cart_service.get_or_create_cart(db, user.id)
    if item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id '{item_id}' not found",
        )

    try:
        item = await cart_service.update_item(db, item_id, data.quantity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    product = await cart_service.get_product_by_id(db, item.product_id)
    product_name = product.name if product else "Unknown"
    product_slug = product.slug if product else ""

    return CartItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=product_name,
        product_slug=product_slug,
        quantity=item.quantity,
        price_at_add=float(item.price_at_add),
        subtotal=float(item.price_at_add) * item.quantity,
    )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    item_id: uuid.UUID,
    db: DbDep,
    user: UserDep,
) -> None:
    item = await cart_service.get_cart_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id '{item_id}' not found",
        )

    cart = await cart_service.get_or_create_cart(db, user.id)
    if item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id '{item_id}' not found",
        )

    await cart_service.remove_item(db, item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: DbDep,
    user: UserDep,
) -> None:
    cart = await cart_service.get_or_create_cart(db, user.id)
    await cart_service.clear_cart(db, cart.id)
