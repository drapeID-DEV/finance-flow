import pytest
from sqlalchemy import delete

from finance_flow.database import async_session_factory
from finance_flow.models.user import User
from finance_flow.repositories.user_repository import UserRepository
from finance_flow.security import verify_password
from finance_flow.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_user() -> None:
    repository = UserRepository()
    service = UserService(repository)

    async with async_session_factory() as session:
        await session.execute(
            delete(User).where(User.email == "register-test@example.com")
        )
        await session.commit()

        user = await service.register(
            session,
            email="register-test@example.com",
            password="test-password",
        )

        await session.commit()

        assert user.id is not None
        assert user.email == "register-test@example.com"
        assert user.role == "user"
        assert user.is_active is True
        assert user.password_hash != "test-password"
        assert verify_password("test-password", user.password_hash)


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    repository = UserRepository()
    service = UserService(repository)

    async with async_session_factory() as session:
        await session.execute(
            delete(User).where(User.email == "duplicate-test@example.com")
        )
        await session.commit()

        await service.register(
            session,
            email="duplicate-test@example.com",
            password="test-password",
        )
        await session.commit()

        with pytest.raises(
            ValueError,
            match="User with this email already exists",
        ):
            await service.register(
                session,
                email="duplicate-test@example.com",
                password="another-password",
            )