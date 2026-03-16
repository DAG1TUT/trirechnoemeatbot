"""
Сервис смен: открытие, закрытие, бизнес-правила.
"""
from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shift import Shift
from core.models.shop import Shop
from repositories import shift_repo, shift_report_repo, shift_report_edit_repo, shop_repo


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
    revenue_meat: float | None = None,
    revenue_store: float | None = None,
    terminal_revenue: float | None = None,
    cash_revenue: float | None = None,
    receipts: float = 0.0,
    surrender_amount: float = 0.0,
) -> bool:
    """Сохранить отчёт по смене и закрыть смену."""
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
        revenue_meat=revenue_meat,
        revenue_store=revenue_store,
        terminal_revenue=terminal_revenue,
        cash_revenue=cash_revenue,
        receipts=receipts,
        surrender_amount=surrender_amount,
    )
    await shift_repo.close_shift(session, shift_id)
    return True


async def get_active_shifts(session: AsyncSession, for_date: date | None = None) -> list[Shift]:
    """Все открытые смены (за дату или все)."""
    return await shift_repo.get_all_open_shifts(session, shift_date=for_date)


async def get_closed_shifts_for_date(session: AsyncSession, report_date: date) -> list[Shift]:
    """Закрытые смены за дату с отчётами."""
    return await shift_repo.get_closed_shifts_by_date(session, report_date)


def can_edit_report(shift: Shift) -> bool:
    """Редактирование отчёта разрешено только в тот же день (до 24:00)."""
    return date.today() == shift.shift_date


async def get_seller_closed_shift_today(
    session: AsyncSession, seller_id: int
) -> Shift | None:
    """Закрытая смена продавца за сегодня (для кнопки «Редактировать отчёт»)."""
    return await shift_repo.get_closed_shift_by_seller_and_date(
        session, seller_id, date.today()
    )


async def update_shift_report_with_log(
    session: AsyncSession,
    report_id: int,
    seller_id: int,
    telegram_id: int,
    full_name: str,
    *,
    revenue: float | None = None,
    revenue_meat: float | None = None,
    revenue_store: float | None = None,
    terminal_revenue: float | None = None,
    cash_revenue: float | None = None,
    receipts: float | None = None,
    surrender_amount: float | None = None,
    cash_balance: float | None = None,
    stock_balance: float | None = None,
    expenses: float | None = None,
    comment: str | None = None,
) -> bool:
    """
    Обновить отчёт и записать правку в историю.
    Передавать только меняющиеся поля. Проверки (смена своя, дата) — в вызывающем коде.
    """
    report = await shift_report_repo.get_report_by_id(session, report_id)
    if not report:
        return False
    changes = {}
    if revenue is not None and report.revenue != revenue:
        changes["revenue"] = {"old": report.revenue, "new": revenue}
    if revenue_meat is not None and report.revenue_meat != revenue_meat:
        changes["revenue_meat"] = {"old": report.revenue_meat, "new": revenue_meat}
    if revenue_store is not None and report.revenue_store != revenue_store:
        changes["revenue_store"] = {"old": report.revenue_store, "new": revenue_store}
    if terminal_revenue is not None and getattr(report, "terminal_revenue", None) != terminal_revenue:
        changes["terminal_revenue"] = {"old": getattr(report, "terminal_revenue", None), "new": terminal_revenue}
    if cash_revenue is not None and getattr(report, "cash_revenue", None) != cash_revenue:
        changes["cash_revenue"] = {"old": getattr(report, "cash_revenue", None), "new": cash_revenue}
    if receipts is not None and getattr(report, "receipts", 0) != receipts:
        changes["receipts"] = {"old": getattr(report, "receipts", 0), "new": receipts}
    if surrender_amount is not None and getattr(report, "surrender_amount", 0) != surrender_amount:
        changes["surrender_amount"] = {"old": getattr(report, "surrender_amount", 0), "new": surrender_amount}
    if cash_balance is not None and report.cash_balance != cash_balance:
        changes["cash_balance"] = {"old": report.cash_balance, "new": cash_balance}
    if stock_balance is not None and report.stock_balance != stock_balance:
        changes["stock_balance"] = {"old": report.stock_balance, "new": stock_balance}
    if expenses is not None and report.expenses != expenses:
        changes["expenses"] = {"old": report.expenses, "new": expenses}
    if comment is not None and report.comment != comment:
        changes["comment"] = {"old": report.comment, "new": comment}
    await shift_report_repo.update_report(
        session,
        report_id,
        revenue=revenue,
        revenue_meat=revenue_meat,
        revenue_store=revenue_store,
        terminal_revenue=terminal_revenue,
        cash_revenue=cash_revenue,
        receipts=receipts,
        surrender_amount=surrender_amount,
        cash_balance=cash_balance,
        stock_balance=stock_balance,
        expenses=expenses,
        comment=comment,
    )
    if changes:
        await shift_report_edit_repo.add_edit(
            session,
            shift_report_id=report_id,
            edited_by_telegram_id=telegram_id,
            edited_by_name=full_name or "",
            changes=changes,
        )
    return True


async def get_shops_for_select(session: AsyncSession) -> list[Shop]:
    """Список торговых точек для выбора."""
    return await shop_repo.get_all_active_shops(session)
