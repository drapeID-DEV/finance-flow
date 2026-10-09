import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from finance_flow.config import get_settings

ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    settings = get_settings()

    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": "access",
        "jti": secrets.token_urlsafe(16),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError:
        return None

    if payload.get("type") != "access":
        return None

    subject = payload.get("sub")

    if not isinstance(subject, str):
        return None

    try:
        return int(subject)
    except ValueError:
        return None


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_refresh_token_expiry() -> datetime:
    settings = get_settings()

    return datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days
    )