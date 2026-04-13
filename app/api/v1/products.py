import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.database import get_db
from app.schemas.product import (
    PaginatedProductsResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductInListResponse,
    ProductResponse,
    ProductUpdate,
    TrendingProductResponse,
)
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
AdminUserDep = Annotated[uuid.UUID, Depends(require_admin)]


@router.get("", response_model=PaginatedProductsResponse)
async def list_products(
    db: DbDep,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[uuid.UUID] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
) -> PaginatedProductsResponse:
    products, total = await product_service.get_products(
        db,
        page=page,
        limit=limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=True,
    )

    total_pages = (total + limit - 1) // limit
    items = [
        ProductInListResponse(
            id=p.id,
            name=p.name,
            slug=p.slug,
            price=float(p.price),
            old_price=float(p.old_price) if p.old_price else None,
            image_url=p.image_url,
        )
        for p in products
    ]

    return PaginatedProductsResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=total_pages,
    )


@router.get("/trending", response_model=list[TrendingProductResponse])
async def get_trending_products(
    db: DbDep,
    limit: int = Query(10, ge=1, le=50),
) -> list[TrendingProductResponse]:
    products = await product_service.get_trending_products(db, limit=limit)

    return [
        TrendingProductResponse(
            product_id=p.id,
            slug=p.slug,
            name=p.name,
            price=float(p.price),
            view_count=0,
            image_url=p.image_url,
        )
        for p in products
    ]


@router.get("/{slug}", response_model=ProductDetailResponse)
async def get_product(
    slug: str,
    db: DbDep,
) -> ProductDetailResponse:
    product = await product_service.get_product_by_slug(db, slug)
    if not product:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with slug '{slug}' not found",
        )

    category_name = None
    if product.category:
        category_name = product.category.name

    return ProductDetailResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        price=float(product.price),
        old_price=float(product.old_price) if product.old_price else None,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        image_url=product.image_url,
        images=product.images or [],
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category_name=category_name,
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: DbDep,
    admin: uuid.UUID = Depends(require_admin),
) -> ProductResponse:
    existing = await product_service.get_product_by_slug(db, data.slug)
    if existing:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this slug already exists",
        )

    product = await product_service.create_product(db, data)
    return ProductResponse.model_validate(product)


@router.patch("/{slug}", response_model=ProductResponse)
async def update_product(
    slug: str,
    data: ProductUpdate,
    db: DbDep,
    admin: uuid.UUID = Depends(require_admin),
) -> ProductResponse:
    product = await product_service.get_product_by_slug_or_404(db, slug)
    product = await product_service.update_product(db, product, data)
    return ProductResponse.model_validate(product)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    slug: str,
    db: DbDep,
    admin: uuid.UUID = Depends(require_admin),
) -> None:
    product = await product_service.get_product_by_slug_or_404(db, slug)
    await product_service.delete_product(db, product)
