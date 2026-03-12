"""
Репозиторий статуса итогового отчёта за день.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.daily_report_status import DailyReportStatus


async def get_status_by_date(session: AsyncSession, report_date: date) -> DailyReportStatus | None:
    """Статус отправки итогового отчёта за дату."""
    result = await session.execute(
        select(DailyReportStatus).where(DailyReportStatus.report_date == report_date)
    )
    return result.scalar_one_or_none()


async def mark_final_sent(session: AsyncSession, report_date: date) -> DailyReportStatus:
    """Отметить, что итоговый отчёт за день отправлен."""
    status = await get_status_by_date(session, report_date)
    if status:
        status.is_final_sent = True
        status.sent_at = datetime.now()
        session.add(status)
        await session.flush()
        await session.refresh(status)
        return status
    status = DailyReportStatus(
        report_date=report_date,
        is_final_sent=True,
        sent_at=datetime.now(),
    )
    session.add(status)
    await session.flush()
    await session.refresh(status)
    return status
