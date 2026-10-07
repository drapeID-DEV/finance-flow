from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.user import User
from finance_flow.repositories.user_repository import UserRepository
from finance_flow.security import hash_password


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register(
        self,
        session: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        existing_user = await self.repository.get_by_email(
            session,
            email,
        )

        if existing_user is not None:
            raise ValueError("User with this email already exists")

        user = User(
            email=email,
            password_hash=hash_password(password),
            role="user",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        return await self.repository.add(session, user)