"""
Репозиторий торговых точек.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shop import Shop


async def get_all_active_shops(session: AsyncSession) -> list[Shop]:
    """Все активные торговые точки."""
    result = await session.execute(
        select(Shop).where(Shop.is_active.is_(True)).order_by(Shop.id)
    )
    return list(result.scalars().all())


async def get_shop_by_id(session: AsyncSession, shop_id: int) -> Shop | None:
    """Найти точку по id."""
    result = await session.execute(select(Shop).where(Shop.id == shop_id))
    return result.scalar_one_or_none()
