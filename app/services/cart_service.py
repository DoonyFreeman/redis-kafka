import uuid

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.cart import CartItem
from app.models.product import Product


async def get_cart_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Cart | None:
    stmt = select(Cart).where(Cart.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_cart(db: AsyncSession, user_id: uuid.UUID) -> Cart:
    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart


async def get_or_create_cart(db: AsyncSession, user_id: uuid.UUID) -> Cart:
    cart = await get_cart_by_user_id(db, user_id)
    if not cart:
        cart = await create_cart(db, user_id)
    return cart


async def get_cart_item_by_id(db: AsyncSession, item_id: uuid.UUID) -> CartItem | None:
    stmt = select(CartItem).where(CartItem.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_cart_item_by_cart_and_product(
    db: AsyncSession, cart_id: uuid.UUID, product_id: uuid.UUID
) -> CartItem | None:
    stmt = select(CartItem).where(
        and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_product_by_id(db: AsyncSession, product_id: uuid.UUID) -> Product | None:
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_item(
    db: AsyncSession,
    cart_id: uuid.UUID,
    product_id: uuid.UUID,
    quantity: int,
) -> CartItem:
    product = await get_product_by_id(db, product_id)
    if not product:
        raise ValueError(f"Product with id {product_id} not found")

    if not product.is_active:
        raise ValueError("Product is not available")

    if product.stock_quantity < quantity:
        raise ValueError(f"Not enough stock. Available: {product.stock_quantity}")

    existing_item = await get_cart_item_by_cart_and_product(db, cart_id, product_id)
    if existing_item:
        new_quantity = existing_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            raise ValueError(f"Not enough stock. Available: {product.stock_quantity}")
        existing_item.quantity = new_quantity
        await db.commit()
        await db.refresh(existing_item)
        return existing_item

    cart_item = CartItem(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
        price_at_add=product.price,
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


async def update_item(
    db: AsyncSession,
    item_id: uuid.UUID,
    quantity: int,
) -> CartItem:
    item = await get_cart_item_by_id(db, item_id)
    if not item:
        raise ValueError(f"Cart item with id {item_id} not found")

    product = await get_product_by_id(db, item.product_id)
    if product and product.stock_quantity < quantity:
        raise ValueError(f"Not enough stock. Available: {product.stock_quantity}")

    item.quantity = quantity
    await db.commit()
    await db.refresh(item)
    return item


async def remove_item(db: AsyncSession, item_id: uuid.UUID) -> bool:
    item = await get_cart_item_by_id(db, item_id)
    if not item:
        return False

    await db.delete(item)
    await db.commit()
    return True


async def clear_cart(db: AsyncSession, cart_id: uuid.UUID) -> None:
    stmt = select(CartItem).where(CartItem.cart_id == cart_id)
    result = await db.execute(stmt)
    items = result.scalars().all()

    for item in items:
        await db.delete(item)

    await db.commit()


async def get_cart_with_items(
    db: AsyncSession, cart_id: uuid.UUID
) -> tuple[Cart, list[CartItem], float]:
    cart_items_stmt = select(CartItem).where(CartItem.cart_id == cart_id)

    result = await db.execute(cart_items_stmt)
    items = list(result.scalars().all())

    total: float = 0.0
    for item in items:
        total += float(item.price_at_add) * item.quantity

    cart_stmt = select(Cart).where(Cart.id == cart_id)
    cart_result = await db.execute(cart_stmt)
    cart = cart_result.scalar_one_or_none()

    if not cart:
        raise ValueError(f"Cart with id {cart_id} not found")

    return cart, items, total


async def get_cart_items(db: AsyncSession, cart_id: uuid.UUID) -> list[CartItem]:
    stmt = select(CartItem).where(CartItem.cart_id == cart_id)

    result = await db.execute(stmt)
    return list(result.scalars().all())
