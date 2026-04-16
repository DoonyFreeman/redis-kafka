import asyncio
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import CartItem
from app.models.order import Order
from app.models.order import OrderItem
from app.models.product import Product
from app.schemas.order import OrderStatus
from app.schemas.order import PaymentStatus


def generate_order_number() -> str:
    now = datetime.utcnow()
    random_part = uuid.uuid4().hex[:8].upper()
    return f"ORD-{now.year}-{random_part}"


async def get_order_by_number(db: AsyncSession, order_number: str) -> Order | None:
    stmt = select(Order).where(Order.order_number == order_number)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_order_by_id(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_orders(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Order], int]:
    count_stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    orders = result.scalars().all()

    return list(orders), total


async def get_cart_items_with_products(
    db: AsyncSession, cart_id: uuid.UUID
) -> list[tuple[CartItem, Product]]:
    stmt = (
        select(CartItem, Product)
        .join(Product, CartItem.product_id == Product.id)
        .where(CartItem.cart_id == cart_id)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [(row[0], row[1]) for row in rows]


async def create_order_from_dict(
    db: AsyncSession,
    user_id: uuid.UUID,
    cart_id: uuid.UUID,
    shipping_address: dict,
    payment_method: str = "card",
    notes: str | None = None,
) -> Order:
    cart_items = await get_cart_items_with_products(db, cart_id)

    if not cart_items:
        raise ValueError("Cannot create order with empty cart")

    total_amount = Decimal("0")
    order_items: list[OrderItem] = []

    for cart_item, product in cart_items:
        item_total = cart_item.price_at_add * cart_item.quantity
        total_amount += item_total

        order_item = OrderItem(
            product_id=cart_item.product_id,
            product_name=product.name,
            quantity=cart_item.quantity,
            unit_price=cart_item.price_at_add,
            total_price=item_total,
        )
        order_items.append(order_item)

        product.stock_quantity = max(0, product.stock_quantity - cart_item.quantity)

    order = Order(
        order_number=generate_order_number(),
        user_id=user_id,
        status=OrderStatus.PENDING.value,
        total_amount=total_amount,
        shipping_address=shipping_address,
        payment_method=payment_method,
        payment_status=PaymentStatus.PENDING.value,
        notes=notes,
    )

    db.add(order)
    await db.flush()

    for item in order_items:
        item.order_id = order.id
        db.add(item)

    for cart_item, _ in cart_items:
        await db.delete(cart_item)

    await db.commit()
    await db.refresh(order)

    return order


async def cancel_order(db: AsyncSession, order_number: str) -> Order:
    order = await get_order_by_number(db, order_number)

    if not order:
        raise ValueError(f"Order with number '{order_number}' not found")

    if order.status not in [OrderStatus.PENDING.value]:
        raise ValueError(
            f"Cannot cancel order with status '{order.status}'. "
            f"Only pending orders can be cancelled."
        )

    for item in order.items:
        if item.product_id:
            product_stmt = select(Product).where(Product.id == item.product_id)
            result = await db.execute(product_stmt)
            product = result.scalar_one_or_none()
            if product:
                product.stock_quantity += item.quantity

    order.status = OrderStatus.CANCELLED.value
    await db.commit()
    await db.refresh(order)

    return order


async def process_payment(order_id: uuid.UUID) -> bool:
    await asyncio.sleep(0.5)
    return True


async def update_order_status(
    db: AsyncSession,
    order: Order,
    status: str,
) -> Order:
    order.status = status
    await db.commit()
    await db.refresh(order)
    return order


async def update_payment_status(
    db: AsyncSession,
    order: Order,
    payment_status: str,
) -> Order:
    order.payment_status = payment_status
    await db.commit()
    await db.refresh(order)
    return order


async def mark_order_as_paid(db: AsyncSession, order_number: str) -> Order:
    order = await get_order_by_number(db, order_number)

    if not order:
        raise ValueError(f"Order with number '{order_number}' not found")

    order.status = OrderStatus.PAID.value
    order.payment_status = PaymentStatus.PAID.value

    await db.commit()
    await db.refresh(order)

    return order
