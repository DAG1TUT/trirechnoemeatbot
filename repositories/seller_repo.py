"""
Репозиторий продавцов.
"""
from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.seller import Seller


async def get_all_active_sellers(session: AsyncSession) -> list[Seller]:
    """Все активные продавцы для выбора при привязке."""
    result = await session.execute(
        select(Seller).where(Seller.is_active.is_(True)).order_by(Seller.id)
    )
    return list(result.scalars().all())


async def get_seller_by_telegram_id(session: AsyncSession, telegram_id: int) -> Seller | None:
    """Найти продавца по telegram_id."""
    result = await session.execute(
        select(Seller).where(Seller.telegram_id == telegram_id, Seller.is_active.is_(True))
    )
    return result.scalar_one_or_none()


async def get_seller_by_id(session: AsyncSession, seller_id: int) -> Seller | None:
    """Найти продавца по id."""
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    return result.scalar_one_or_none()


async def bind_telegram_to_seller(session: AsyncSession, seller_id: int, telegram_id: int) -> Seller | None:
    """Привязать telegram_id к продавцу. Возвращает обновлённого продавца."""
    seller = await get_seller_by_id(session, seller_id)
    if not seller:
        return None
    seller.telegram_id = telegram_id
    session.add(seller)
    await session.flush()
    await session.refresh(seller)
    return seller


async def get_all_sellers(session: AsyncSession) -> list[Seller]:
    """Все продавцы (включая неактивных) для административного управления."""
    result = await session.execute(select(Seller).order_by(Seller.id))
    return list(result.scalars().all())


async def create_seller(session: AsyncSession, full_name: str) -> Seller:
    """Создать нового продавца."""
    seller = Seller(full_name=full_name.strip(), is_active=True)
    session.add(seller)
    await session.flush()
    await session.refresh(seller)
    return seller


async def update_seller_name(session: AsyncSession, seller_id: int, full_name: str) -> Seller | None:
    """Обновить ФИО продавца."""
    seller = await get_seller_by_id(session, seller_id)
    if not seller:
        return None
    seller.full_name = full_name.strip()
    session.add(seller)
    await session.flush()
    await session.refresh(seller)
    return seller


async def set_seller_active(session: AsyncSession, seller_id: int, is_active: bool) -> Seller | None:
    """Активировать/деактивировать продавца."""
    seller = await get_seller_by_id(session, seller_id)
    if not seller:
        return None
    seller.is_active = is_active
    session.add(seller)
    await session.flush()
    await session.refresh(seller)
    return seller


async def get_sellers_available_for_web_registration(session: AsyncSession) -> list[Seller]:
    """Активные продавцы без веб-пароля — можно выбрать при регистрации на сайте."""
    result = await session.execute(
        select(Seller)
        .where(
            Seller.is_active.is_(True),
            or_(Seller.web_password_hash.is_(None), Seller.web_password_hash == ""),
        )
        .order_by(Seller.id)
    )
    return list(result.scalars().all())


async def set_web_password_hash(session: AsyncSession, seller_id: int, password_hash: str) -> Seller | None:
    """Установить хэш пароля для веб-кабинета."""
    seller = await get_seller_by_id(session, seller_id)
    if not seller or not seller.is_active:
        return None
    seller.web_password_hash = password_hash
    session.add(seller)
    await session.flush()
    await session.refresh(seller)
    return seller


async def clear_web_password(session: AsyncSession, seller_id: int) -> Seller | None:
    """Сбросить веб-вход (отвязать сайт от продавца)."""
    seller = await get_seller_by_id(session, seller_id)
    if not seller:
        return None
    seller.web_password_hash = None
    session.add(seller)
    await session.flush()
    await session.refresh(seller)
    return seller
