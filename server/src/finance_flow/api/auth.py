from datetime import UTC, datetime

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.auth import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token,
)
from finance_flow.dependencies import get_current_user, get_db_session
from finance_flow.models.refresh_token import RefreshToken
from finance_flow.models.user import User
from finance_flow.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from finance_flow.repositories.user_repository import UserRepository
from finance_flow.security import verify_password
from finance_flow.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

repository = UserRepository()
refresh_token_repository = RefreshTokenRepository()
service = UserService(repository)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> RegisterResponse:
    try:
        user = await service.register(
            session,
            email=str(data.email),
            password=data.password,
        )
        await session.commit()
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return RegisterResponse(
        id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    user = await repository.get_by_email(
        session,
        str(data.email),
    )

    if user is None or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    refresh_token = create_refresh_token()
    now = datetime.now(UTC)

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=get_refresh_token_expiry(),
        created_at=now,
    )

    await refresh_token_repository.add(
        session,
        refresh_token_record,
    )
    await session.commit()

    access_token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return LoginResponse(message="Login successful")



@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    now = datetime.now(UTC)
    token_hash = hash_refresh_token(refresh_token)

    token_record = await refresh_token_repository.consume_by_hash(
        session,
        token_hash,
        now,
    )

    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = await repository.get_by_id(session, token_record.user_id)

    if user is None or not user.is_active:
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user",
        )

    new_refresh_token = create_refresh_token()
    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh_token),
        expires_at=get_refresh_token_expiry(),
        created_at=now,
    )

    try:
        await refresh_token_repository.add(
            session,
            new_token_record,
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    access_token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return LoginResponse(message="Tokens refreshed successfully")



@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    if refresh_token is not None:
        token_hash = hash_refresh_token(refresh_token)

        await refresh_token_repository.delete_by_hash(
            session,
            token_hash,
        )
        await session.commit()

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/api/v1/auth",
    )

    return {"message": "Logout successful"}


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }