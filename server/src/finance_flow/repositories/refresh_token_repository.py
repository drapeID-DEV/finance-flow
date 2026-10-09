from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_flow.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    async def get_by_hash(
        self,
        session: AsyncSession,
        token_hash: str,
    ) -> RefreshToken | None:
        result = await session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def add(
        self,
        session: AsyncSession,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        session.add(refresh_token)
        await session.flush()
        return refresh_token

    async def delete_by_hash(
        self,
        session: AsyncSession,
        token_hash: str,
    ) -> None:
        await session.execute(
            delete(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )

    async def delete_expired(
        self,
        session: AsyncSession,
        now: datetime,
    ) -> int:
        result = await session.execute(
            select(RefreshToken.id).where(
                RefreshToken.expires_at <= now
            )
        )
        expired_ids = result.scalars().all()

        if not expired_ids:
            return 0

        await session.execute(
            delete(RefreshToken).where(
                RefreshToken.id.in_(expired_ids)
            )
        )

        return len(expired_ids)

    async def consume_by_hash(
        self,
        session: AsyncSession,
        token_hash: str,
        now: datetime,
    ) -> RefreshToken | None:
        result = await session.execute(
            delete(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.expires_at > now,
            )
            .returning(RefreshToken)
        )
        return result.scalar_one_or_none()