import pytest


class TestProductServiceImports:
    def test_product_service_module_exists(self):
        from app.services import product_service

        assert product_service is not None

    def test_product_service_functions_exist(self):
        from app.services import product_service

        assert hasattr(product_service, "get_products")
        assert hasattr(product_service, "get_product_by_id")
        assert hasattr(product_service, "get_product_by_slug")
        assert hasattr(product_service, "get_trending_products")
        assert hasattr(product_service, "create_product")
        assert hasattr(product_service, "update_product")
        assert hasattr(product_service, "delete_product")

    def test_product_model_importable(self):
        from app.models.product import Product

        assert Product is not None

    def test_product_schemas_importable(self):
        from app.schemas.product import ProductCreate
        from app.schemas.product import ProductUpdate

        assert ProductCreate is not None
        assert ProductUpdate is not None

    def test_cache_service_importable(self):
        from app.services import cache_service

        assert cache_service is not None


class TestProductSchemaValidation:
    def test_product_create_schema(self):
        from app.schemas.product import ProductCreate

        product = ProductCreate(
            name="Test Product",
            slug="test-product",
            description="Test description",
            price=99.99,
            stock_quantity=10,
        )
        assert product.name == "Test Product"
        assert product.slug == "test-product"
        assert product.price == 99.99

    def test_product_create_with_optional_fields(self):
        from app.schemas.product import ProductCreate

        product = ProductCreate(
            name="Test Product",
            slug="test-product",
            description="Test description",
            price=99.99,
            old_price=129.99,
            stock_quantity=10,
            image_url="https://example.com/image.jpg",
        )
        assert product.old_price == 129.99
        assert product.image_url == "https://example.com/image.jpg"

    def test_product_create_with_category(self):
        import uuid

        from app.schemas.product import ProductCreate

        category_id = uuid.uuid4()
        product = ProductCreate(
            name="Test Product",
            slug="test-product",
            description="Test description",
            price=99.99,
            stock_quantity=10,
            category_id=category_id,
        )
        assert product.category_id == category_id


class TestProductModelStructure:
    def test_product_model_has_required_fields(self):
        from app.models.product import Product

        assert hasattr(Product, "id")
        assert hasattr(Product, "name")
        assert hasattr(Product, "slug")
        assert hasattr(Product, "price")
        assert hasattr(Product, "stock_quantity")
        assert hasattr(Product, "is_active")


class TestProductSlugValidation:
    def test_slug_is_converted_to_lowercase(self):
        from app.schemas.product import ProductCreate

        product = ProductCreate(
            name="Test Product",
            slug="TEST-PRODUCT",
            price=99.99,
            stock_quantity=10,
        )
        assert product.slug == "test-product"

    def test_slug_replaces_spaces_with_dashes(self):
        from app.schemas.product import ProductCreate

        product = ProductCreate(
            name="Test Product",
            slug="test product slug",
            price=99.99,
            stock_quantity=10,
        )
        assert product.slug == "test-product-slug"


class TestProductPriceValidation:
    def test_price_must_be_positive(self):
        from pydantic import ValidationError

        from app.schemas.product import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test",
                slug="test",
                price=-10,
                stock_quantity=5,
            )

    def test_price_zero_raises_error(self):
        from pydantic import ValidationError

        from app.schemas.product import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test",
                slug="test",
                price=0,
                stock_quantity=5,
            )


class TestProductStockValidation:
    def test_stock_quantity_must_be_non_negative(self):
        from pydantic import ValidationError

        from app.schemas.product import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test",
                slug="test",
                price=10,
                stock_quantity=-5,
            )


class TestProductUpdateSchema:
    def test_product_update_allows_partial_updates(self):
        from app.schemas.product import ProductUpdate

        update = ProductUpdate(name="New Name", price=50.0)
        assert update.name == "New Name"
        assert update.price == 50.0
        assert update.description is None
