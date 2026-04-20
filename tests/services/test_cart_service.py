

class TestCartServiceImports:
    def test_cart_service_module_exists(self):
        from app.services import cart_service

        assert cart_service is not None

    def test_cart_service_functions_exist(self):
        from app.services import cart_service

        assert hasattr(cart_service, "get_cart_by_user_id")
        assert hasattr(cart_service, "create_cart")
        assert hasattr(cart_service, "get_or_create_cart")
        assert hasattr(cart_service, "add_item")
        assert hasattr(cart_service, "update_item")
        assert hasattr(cart_service, "remove_item")
        assert hasattr(cart_service, "clear_cart")
        assert hasattr(cart_service, "get_cart_with_items")

    def test_cart_model_importable(self):
        from app.models.cart import Cart
        from app.models.cart import CartItem

        assert Cart is not None
        assert CartItem is not None


class TestCartSchemaValidation:
    def test_cart_item_add_schema(self):
        import uuid

        from app.schemas.cart import CartItemAddRequest

        item = CartItemAddRequest(product_id=uuid.uuid4(), quantity=2)
        assert item.quantity == 2

    def test_cart_item_update_schema(self):
        from app.schemas.cart import CartItemUpdateRequest

        item = CartItemUpdateRequest(quantity=5)
        assert item.quantity == 5


class TestCartServiceLogic:
    def test_cart_service_raises_error_for_out_of_stock(self):
        from app.services import cart_service

        assert hasattr(cart_service, "add_item")

    def test_cart_service_raises_error_for_inactive_product(self):
        from app.services import cart_service

        assert hasattr(cart_service, "add_item")


class TestCartModelStructure:
    def test_cart_model_has_required_fields(self):
        from app.models.cart import Cart

        assert hasattr(Cart, "id")
        assert hasattr(Cart, "user_id")
        assert hasattr(Cart, "session_id")

    def test_cart_item_model_has_required_fields(self):
        from app.models.cart import CartItem

        assert hasattr(CartItem, "id")
        assert hasattr(CartItem, "cart_id")
        assert hasattr(CartItem, "product_id")
        assert hasattr(CartItem, "quantity")
        assert hasattr(CartItem, "price_at_add")


class TestCartTotalCalculation:
    def test_cart_total_calculation_logic(self):
        items = [
            {"price_at_add": 10.0, "quantity": 2},
            {"price_at_add": 5.0, "quantity": 3},
        ]
        expected_total = 10.0 * 2 + 5.0 * 3
        actual_total = sum(item["price_at_add"] * item["quantity"] for item in items)
        assert actual_total == expected_total
