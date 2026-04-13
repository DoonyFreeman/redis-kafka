import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, Category
from app.schemas.product import ProductCreate, ProductUpdate


async def get_products(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    category_id: uuid.UUID | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    is_active: bool | None = True,
) -> tuple[Sequence[Product], int]:
    base_conditions = []
    if is_active is not None:
        base_conditions.append(Product.is_active == is_active)
    if category_id:
        base_conditions.append(Product.category_id == category_id)
    if min_price is not None:
        base_conditions.append(Product.price >= min_price)
    if max_price is not None:
        base_conditions.append(Product.price <= max_price)

    count_stmt = select(func.count()).select_from(Product)
    if base_conditions:
        count_stmt = count_stmt.where(and_(*base_conditions))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    stmt = select(Product).order_by(Product.created_at.desc())
    if base_conditions:
        stmt = stmt.where(and_(*base_conditions))
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    products = result.scalars().all()
    return products, total


async def get_product_by_id(db: AsyncSession, product_id: uuid.UUID) -> Product | None:
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_product_by_slug(db: AsyncSession, slug: str) -> Product | None:
    stmt = select(Product).where(Product.slug == slug)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_product_by_slug_or_404(
    db: AsyncSession,
    slug: str,
) -> Product:
    product = await get_product_by_slug(db, slug)
    if not product:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with slug '{slug}' not found",
        )
    return product


async def get_trending_products(
    db: AsyncSession,
    limit: int = 10,
) -> Sequence[Product]:
    stmt = (
        select(Product)
        .where(
            Product.is_active == True,
            Product.stock_quantity > 0,
        )
        .order_by(Product.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_product(
    db: AsyncSession,
    data: ProductCreate,
) -> Product:
    product = Product(
        name=data.name,
        slug=data.slug,
        description=data.description,
        price=Decimal(str(data.price)),
        old_price=Decimal(str(data.old_price)) if data.old_price else None,
        stock_quantity=data.stock_quantity,
        category_id=data.category_id,
        image_url=data.image_url,
        images=data.images,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(
    db: AsyncSession,
    product: Product,
    data: ProductUpdate,
) -> Product:
    update_data = data.model_dump(exclude_unset=True)
    if "price" in update_data and update_data["price"] is not None:
        update_data["price"] = Decimal(str(update_data["price"]))
    if "old_price" in update_data and update_data["old_price"] is not None:
        update_data["old_price"] = Decimal(str(update_data["old_price"]))

    for field, value in update_data.items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(
    db: AsyncSession,
    product: Product,
) -> None:
    await db.delete(product)
    await db.commit()


async def get_products_by_category(
    db: AsyncSession,
    category_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> Sequence[Product]:
    stmt = (
        select(Product)
        .where(
            Product.category_id == category_id,
            Product.is_active == True,
        )
        .order_by(Product.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_active_products_count(db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Product).where(Product.is_active == True)
    result = await db.execute(stmt)
    return result.scalar() or 0
