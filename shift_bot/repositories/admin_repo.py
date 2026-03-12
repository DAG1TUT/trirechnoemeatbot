"""
Репозиторий администраторов.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.admin import Admin


async def get_admin_by_telegram_id(session: AsyncSession, telegram_id: int) -> Admin | None:
    """Найти админа по telegram_id."""
    result = await session.execute(
        select(Admin).where(Admin.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_all_admin_telegram_ids(session: AsyncSession) -> list[int]:
    """Список telegram_id всех админов (для рассылки)."""
    result = await session.execute(select(Admin.telegram_id))
    return list(result.scalars().all())
