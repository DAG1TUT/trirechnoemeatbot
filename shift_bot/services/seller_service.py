"""
Сервис продавцов: привязка Telegram, проверки.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.seller import Seller
from repositories import seller_repo


async def get_seller_by_telegram(session: AsyncSession, telegram_id: int) -> Seller | None:
    """Получить продавца по telegram_id."""
    return await seller_repo.get_seller_by_telegram_id(session, telegram_id)


async def get_sellers_for_binding(session: AsyncSession) -> list[Seller]:
    """Список продавцов для выбора при привязке (все активные)."""
    return await seller_repo.get_all_active_sellers(session)


async def bind_seller(session: AsyncSession, seller_id: int, telegram_id: int) -> Seller | None:
    """Привязать telegram_id к продавцу. Возвращает продавца или None."""
    return await seller_repo.bind_telegram_to_seller(session, seller_id, telegram_id)
