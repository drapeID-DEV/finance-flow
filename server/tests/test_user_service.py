import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.user import User
from finance_flow.repositories.user_repository import UserRepository
from finance_flow.security import verify_password
from finance_flow.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_user(db_session: AsyncSession) -> None:
    repository = UserRepository()
    service = UserService(repository)

    await db_session.execute(
        delete(User).where(User.email == "register-test@example.com")
    )
    await db_session.flush()

    user = await service.register(
        db_session,
        email="register-test@example.com",
        password="test-password",
    )

    await db_session.flush()

    assert user.id is not None
    assert user.email == "register-test@example.com"
    assert user.role == "user"
    assert user.is_active is True
    assert user.password_hash != "test-password"
    assert verify_password("test-password", user.password_hash)


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session: AsyncSession) -> None:
    repository = UserRepository()
    service = UserService(repository)

    await db_session.execute(
        delete(User).where(User.email == "duplicate-test@example.com")
    )
    await db_session.flush()

    await service.register(
        db_session,
        email="duplicate-test@example.com",
        password="test-password",
    )
    await db_session.flush()

    with pytest.raises(
        ValueError,
        match="User with this email already exists",
    ):
        await service.register(
            db_session,
            email="duplicate-test@example.com",
            password="another-password",
        )