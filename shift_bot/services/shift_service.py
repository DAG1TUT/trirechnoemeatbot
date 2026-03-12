"""
Сервис смен: открытие, закрытие, бизнес-правила.
"""
from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shift import Shift
from core.models.shop import Shop
from repositories import shift_repo, shift_report_repo, shop_repo


class ShiftError(Exception):
    """Ошибка бизнес-логики смены."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


async def open_shift(
    session: AsyncSession,
    seller_id: int,
    shop_id: int,
    shift_date: date | None = None,
) -> Shift:
    """
    Открыть смену. Проверяет:
    - у продавца нет другой открытой смены;
    - точка не занята.
    """
    shift_date = shift_date or date.today()
    existing = await shift_repo.get_open_shift_by_seller_id(session, seller_id)
    if existing:
        raise ShiftError("У вас уже есть открытая смена. Сначала закройте её.")
    occupied = await shift_repo.get_open_shift_by_shop_id(session, shop_id)
    if occupied:
        raise ShiftError("Эта торговая точка уже занята другим продавцом.")
    shift = await shift_repo.create_shift(
        session,
        seller_id=seller_id,
        shop_id=shop_id,
        shift_date=shift_date,
        open_time=datetime.now().time(),
    )
    return shift


async def get_current_shift(session: AsyncSession, seller_id: int) -> Shift | None:
    """Текущая открытая смена продавца."""
    return await shift_repo.get_open_shift_by_seller_id(session, seller_id)


async def close_shift(session: AsyncSession, shift_id: int, seller_id: int) -> Shift | None:
    """
    Закрыть смену. Только свою и только открытую.
    """
    shift = await shift_repo.get_shift_by_id(session, shift_id)
    if not shift:
        return None
    if shift.seller_id != seller_id:
        return None
    if shift.status != "open":
        return None
    return await shift_repo.close_shift(session, shift_id)


async def save_shift_report(
    session: AsyncSession,
    shift_id: int,
    seller_id: int,
    revenue: float,
    cash_balance: float,
    stock_balance: float,
    expenses: float,
    comment: str = "",
) -> bool:
    """Сохранить отчёт по смене и закрыть смену. Проверяет, что смена своя и открыта."""
    shift = await shift_repo.get_shift_by_id(session, shift_id)
    if not shift or shift.seller_id != seller_id or shift.status != "open":
        return False
    await shift_report_repo.create_shift_report(
        session,
        shift_id=shift_id,
        revenue=revenue,
        cash_balance=cash_balance,
        stock_balance=stock_balance,
        expenses=expenses,
        comment=comment,
    )
    await shift_repo.close_shift(session, shift_id)
    return True


async def get_active_shifts(session: AsyncSession, for_date: date | None = None) -> list[Shift]:
    """Все открытые смены (за дату или все)."""
    return await shift_repo.get_all_open_shifts(session, shift_date=for_date)


async def get_closed_shifts_for_date(session: AsyncSession, report_date: date) -> list[Shift]:
    """Закрытые смены за дату с отчётами."""
    return await shift_repo.get_closed_shifts_by_date(session, report_date)


async def get_shops_for_select(session: AsyncSession) -> list[Shop]:
    """Список торговых точек для выбора."""
    return await shop_repo.get_all_active_shops(session)
