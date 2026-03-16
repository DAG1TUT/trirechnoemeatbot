"""
Репозиторий отчётов по сменам.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shift_report import ShiftReport


async def get_report_by_id(session: AsyncSession, report_id: int) -> ShiftReport | None:
    """Отчёт по id."""
    result = await session.execute(
        select(ShiftReport).where(ShiftReport.id == report_id)
    )
    return result.scalar_one_or_none()


async def create_shift_report(
    session: AsyncSession,
    shift_id: int,
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
) -> ShiftReport:
    """Создать отчёт по смене."""
    report = ShiftReport(
        shift_id=shift_id,
        revenue=revenue,
        cash_balance=cash_balance,
        stock_balance=stock_balance,
        expenses=expenses,
        comment=comment or "",
        revenue_meat=revenue_meat,
        revenue_store=revenue_store,
        terminal_revenue=terminal_revenue,
        cash_revenue=cash_revenue,
        receipts=receipts,
        surrender_amount=surrender_amount,
    )
    session.add(report)
    await session.flush()
    await session.refresh(report)
    return report


async def get_report_by_shift_id(session: AsyncSession, shift_id: int) -> ShiftReport | None:
    """Отчёт по смене."""
    result = await session.execute(
        select(ShiftReport).where(ShiftReport.shift_id == shift_id)
    )
    return result.scalar_one_or_none()


async def update_report(
    session: AsyncSession,
    report_id: int,
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
) -> ShiftReport | None:
    """Обновить поля отчёта. Передавать только меняющиеся поля."""
    report = await get_report_by_id(session, report_id)
    if not report:
        return None
    if revenue is not None:
        report.revenue = revenue
    if revenue_meat is not None:
        report.revenue_meat = revenue_meat
    if revenue_store is not None:
        report.revenue_store = revenue_store
    if terminal_revenue is not None:
        report.terminal_revenue = terminal_revenue
    if cash_revenue is not None:
        report.cash_revenue = cash_revenue
    if receipts is not None:
        report.receipts = receipts
    if surrender_amount is not None:
        report.surrender_amount = surrender_amount
    if cash_balance is not None:
        report.cash_balance = cash_balance
    if stock_balance is not None:
        report.stock_balance = stock_balance
    if expenses is not None:
        report.expenses = expenses
    if comment is not None:
        report.comment = comment
    session.add(report)
    await session.flush()
    await session.refresh(report)
    return report
