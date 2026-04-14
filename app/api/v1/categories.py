import uuid
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.database import get_db
from app.schemas.category import CategoryCreate
from app.schemas.category import CategoryResponse
from app.schemas.category import CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
AdminUserDep = Annotated[uuid.UUID, Depends(require_admin)]


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    db: DbDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> list[CategoryResponse]:
    categories = await category_service.get_categories(
        db,
        skip=skip,
        limit=limit,
        include_inactive=False,
    )
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(
    slug: str,
    db: DbDep,
) -> CategoryResponse:
    category = await category_service.get_category_by_slug(db, slug)
    if not category:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug '{slug}' not found",
        )
    return CategoryResponse.model_validate(category)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: DbDep,
    admin: uuid.UUID = Depends(require_admin),
) -> CategoryResponse:
    existing = await category_service.get_category_by_slug(db, data.slug)
    if existing:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this slug already exists",
        )

    category = await category_service.create_category(db, data)
    return CategoryResponse.model_validate(category)


@router.patch("/{slug}", response_model=CategoryResponse)
async def update_category(
    slug: str,
    data: CategoryUpdate,
    db: DbDep,
    admin: uuid.UUID = Depends(require_admin),
) -> CategoryResponse:
    category = await category_service.get_category_by_slug_or_404(db, slug)
    category = await category_service.update_category(db, category, data)
    return CategoryResponse.model_validate(category)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    slug: str,
    db: DbDep,
    admin: uuid.UUID = Depends(require_admin),
) -> None:
    category = await category_service.get_category_by_slug_or_404(db, slug)
    await category_service.delete_category(db, category)
