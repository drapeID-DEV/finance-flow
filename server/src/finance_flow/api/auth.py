from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.auth import create_access_token
from finance_flow.dependencies import get_current_user, get_db_session
from finance_flow.models.user import User
from finance_flow.repositories.user_repository import UserRepository
from finance_flow.security import verify_password
from finance_flow.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

repository = UserRepository()
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

    access_token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60,
    )

    return LoginResponse(
        message="Login successful",
    )


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
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