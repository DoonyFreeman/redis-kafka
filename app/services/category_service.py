import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> Sequence[Category]:
    stmt = select(Category).order_by(Category.name)
    if not include_inactive:
        stmt = stmt.where(Category.is_active == True)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_category_by_id(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category | None:
    stmt = select(Category).where(Category.slug == slug)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_category_by_slug_or_404(
    db: AsyncSession,
    slug: str,
) -> Category:
    category = await get_category_by_slug(db, slug)
    if not category:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug '{slug}' not found",
        )
    return category


async def create_category(
    db: AsyncSession,
    data: CategoryCreate,
) -> Category:
    category = Category(
        name=data.name,
        slug=data.slug,
        description=data.description,
        parent_id=data.parent_id,
        image_url=data.image_url,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    category: Category,
    data: CategoryUpdate,
) -> Category:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(
    db: AsyncSession,
    category: Category,
) -> None:
    await db.delete(category)
    await db.commit()


async def get_category_tree(
    db: AsyncSession,
) -> list[Category]:
    stmt = (
        select(Category)
        .where(
            Category.parent_id == None,
            Category.is_active == True,
        )
        .order_by(Category.name)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
