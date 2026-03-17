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


async def get_all_shops(session: AsyncSession) -> list[Shop]:
    """Все торговые точки (включая неактивные) для административного управления."""
    result = await session.execute(select(Shop).order_by(Shop.id))
    return list(result.scalars().all())


async def create_shop(session: AsyncSession, address: str) -> Shop:
    """Создать новую торговую точку."""
    shop = Shop(address=address.strip(), is_active=True)
    session.add(shop)
    await session.flush()
    await session.refresh(shop)
    return shop


async def update_shop_address(session: AsyncSession, shop_id: int, address: str) -> Shop | None:
    """Обновить адрес торговой точки."""
    shop = await get_shop_by_id(session, shop_id)
    if not shop:
        return None
    shop.address = address.strip()
    session.add(shop)
    await session.flush()
    await session.refresh(shop)
    return shop


async def set_shop_active(session: AsyncSession, shop_id: int, is_active: bool) -> Shop | None:
    """Активировать/деактивировать торговую точку."""
    shop = await get_shop_by_id(session, shop_id)
    if not shop:
        return None
    shop.is_active = is_active
    session.add(shop)
    await session.flush()
    await session.refresh(shop)
    return shop
