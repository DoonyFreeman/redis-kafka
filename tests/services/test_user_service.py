import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.user import UserCreate, UserUpdate


class TestUserServiceImports:
    def test_exceptions_importable(self):
        from app.core.exceptions import ConflictError, NotFoundError

        assert ConflictError is not None
        assert NotFoundError is not None

    def test_user_service_class_exists(self):
        from app.services.user_service import UserService

        assert UserService is not None

    def test_user_schemas_importable(self):
        from app.schemas.user import UserCreate, UserUpdate

        assert UserCreate is not None
        assert UserUpdate is not None

    def test_password_hashing(self):
        from app.core.security import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_token_creation(self):
        from datetime import timedelta
        from app.core.security import create_access_token

        token = create_access_token("test@example.com", expires_delta=timedelta(minutes=60))
        assert token is not None
        assert isinstance(token, str)

    def test_get_db_dependency(self):
        from app.database import get_db

        assert get_db is not None


class TestPasswordValidation:
    def test_password_validation_pydantic(self):
        from pydantic import ValidationError

        valid_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123",
        )
        assert valid_data.email == "test@example.com"

        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",
                username="testuser",
                password="password123",
            )


class TestExceptionHandling:
    def test_conflict_error_status_code(self):
        error = ConflictError("Email already registered")
        assert error.status_code == 409

    def test_not_found_error_status_code(self):
        error = NotFoundError("User not found")
        assert error.status_code == 404
