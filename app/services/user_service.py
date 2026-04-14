from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.core.exceptions import NotFoundError
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, user_data: UserCreate) -> User:
        existing_email = await self.get_by_email(user_data.email)
        if existing_email:
            raise ConflictError("Email already registered")

        existing_username = await self.get_by_username(user_data.username)
        if existing_username:
            raise ConflictError("Username already taken")

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)

        if user_data.email and user_data.email != user.email:
            existing = await self.get_by_email(user_data.email)
            if existing:
                raise ConflictError("Email already registered")
            user.email = user_data.email

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "email":
                setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        await self.db.delete(user)
        await self.db.flush()

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
