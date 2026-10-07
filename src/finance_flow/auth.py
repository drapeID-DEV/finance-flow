from datetime import UTC, datetime, timedelta

import jwt

from finance_flow.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user_id: int) -> str:
    settings = get_settings()

    expires_at = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
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

    subject = payload.get("sub")

    if not isinstance(subject, str):
        return None

    try:
        return int(subject)
    except ValueError:
        return None