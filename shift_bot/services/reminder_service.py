"""
Сервис напоминаний: незакрытые смены, уведомления продавцам и админу.
Готов к подключению APScheduler/cron: вызывать функции по расписанию.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shop import Shop
from core.models.shift import Shift
from repositories import shift_repo, shop_repo


async def get_open_shifts_today(session: AsyncSession) -> list:
    """
    Все открытые смены за сегодня.
    Возвращает список смен с загруженными seller, shop.
    """
    return await shift_repo.get_all_open_shifts(session, shift_date=date.today())


async def get_unclosed_shops_today(session: AsyncSession) -> list[Shop]:
    """
    Торговые точки, по которым сегодня ещё нет закрытой смены.
    Для админа: «незакрытые точки» с адресами.
    """
    all_shops = await shop_repo.get_all_active_shops(session)
    all_ids = {s.id for s in all_shops}
    result = await session.execute(
        select(Shift.shop_id).where(
            Shift.shift_date == date.today(),
            Shift.status == "closed",
        ).distinct()
    )
    closed_ids = set(result.scalars().all())
    unclosed_ids = all_ids - closed_ids
    return [s for s in all_shops if s.id in unclosed_ids]
