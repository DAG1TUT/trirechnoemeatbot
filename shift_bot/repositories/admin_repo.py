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


async def ensure_admin(session: AsyncSession, telegram_id: int, full_name: str = "") -> Admin:
    """Добавить админа по telegram_id, если его ещё нет. Возвращает запись."""
    existing = await get_admin_by_telegram_id(session, telegram_id)
    if existing:
        return existing
    admin = Admin(telegram_id=telegram_id, full_name=full_name or "Руководитель")
    session.add(admin)
    await session.flush()
    await session.refresh(admin)
    return admin


async def remove_admin_by_telegram_id(session: AsyncSession, telegram_id: int) -> bool:
    """Удалить админа из БД по telegram_id. Возвращает True, если запись была и удалена."""
    admin = await get_admin_by_telegram_id(session, telegram_id)
    if not admin:
        return False
    await session.delete(admin)
    return True
