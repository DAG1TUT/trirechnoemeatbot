"""
Репозиторий отчётов по сменам.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shift_report import ShiftReport


async def create_shift_report(
    session: AsyncSession,
    shift_id: int,
    revenue: float,
    cash_balance: float,
    stock_balance: float,
    expenses: float,
    comment: str = "",
) -> ShiftReport:
    """Создать отчёт по смене."""
    report = ShiftReport(
        shift_id=shift_id,
        revenue=revenue,
        cash_balance=cash_balance,
        stock_balance=stock_balance,
        expenses=expenses,
        comment=comment or "",
    )
    session.add(report)
    await session.flush()
    await session.refresh(report)
    return report


async def get_report_by_shift_id(session: AsyncSession, shift_id: int) -> ShiftReport | None:
    """Отчёт по смене."""
    from sqlalchemy import select
    result = await session.execute(
        select(ShiftReport).where(ShiftReport.shift_id == shift_id)
    )
    return result.scalar_one_or_none()
