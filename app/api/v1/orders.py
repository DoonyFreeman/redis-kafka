from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.core.kafka import kafka_producer
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreateRequest
from app.schemas.order import OrderItemResponse
from app.schemas.order import OrderListResponse
from app.schemas.order import OrderResponse
from app.services import cart_service
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_active_user)]


def order_to_response(order) -> OrderResponse:
    items = [
        OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=float(item.unit_price),
            total_price=float(item.total_price),
        )
        for item in order.items
    ]

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        status=order.status,
        total_amount=float(order.total_amount),
        shipping_address=order.shipping_address,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        notes=order.notes,
        items=items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("", response_model=OrderListResponse)
async def list_orders(
    db: DbDep,
    user: UserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> OrderListResponse:
    orders, total = await order_service.get_user_orders(db, user.id, page, limit)
    total_pages = (total + limit - 1) // limit

    return OrderListResponse(
        orders=[order_to_response(o) for o in orders],
        total=total,
        page=page,
        limit=limit,
        pages=total_pages,
    )


@router.get("/{order_number}", response_model=OrderResponse)
async def get_order(
    order_number: str,
    db: DbDep,
    user: UserDep,
) -> OrderResponse:
    order = await order_service.get_order_by_number(db, order_number)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number '{order_number}' not found",
        )

    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number '{order_number}' not found",
        )

    return order_to_response(order)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreateRequest,
    db: DbDep,
    user: UserDep,
) -> OrderResponse:
    cart = await cart_service.get_or_create_cart(db, user.id)
    items = await cart_service.get_cart_items(db, cart.id)

    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create order with empty cart",
        )

    try:
        order = await order_service.create_order(db, user.id, cart.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        await kafka_producer.send(
            "order.created",
            {
                "order_number": order.order_number,
                "user_id": str(user.id),
                "total_amount": str(order.total_amount),
                "items_count": len(order.items),
            },
        )
    except Exception:
        pass

    return order_to_response(order)


@router.patch("/{order_number}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_number: str,
    db: DbDep,
    user: UserDep,
) -> OrderResponse:
    order = await order_service.get_order_by_number(db, order_number)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number '{order_number}' not found",
        )

    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number '{order_number}' not found",
        )

    try:
        order = await order_service.cancel_order(db, order_number)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        await kafka_producer.send(
            "order.cancelled",
            {
                "order_number": order.order_number,
                "user_id": str(user.id),
            },
        )
    except Exception:
        pass

    return order_to_response(order)


@router.post("/{order_number}/pay", response_model=OrderResponse)
async def pay_order(
    order_number: str,
    db: DbDep,
    user: UserDep,
) -> OrderResponse:
    order = await order_service.get_order_by_number(db, order_number)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number '{order_number}' not found",
        )

    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number '{order_number}' not found",
        )

    success = await order_service.process_payment(order.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment failed",
        )

    order = await order_service.mark_order_as_paid(db, order_number)

    try:
        await kafka_producer.send(
            "order.paid",
            {
                "order_number": order.order_number,
                "user_id": str(user.id),
                "total_amount": str(order.total_amount),
            },
        )
    except Exception:
        pass

    return order_to_response(order)
