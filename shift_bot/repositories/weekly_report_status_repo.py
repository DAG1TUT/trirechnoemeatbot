"""
Репозиторий статуса недельной аналитики.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.weekly_report_status import WeeklyReportStatus


async def get_status_by_week_end(session: AsyncSession, week_end_date: date) -> WeeklyReportStatus | None:
    """Статус отправки недельной аналитики за неделю (дата воскресенья)."""
    result = await session.execute(
        select(WeeklyReportStatus).where(WeeklyReportStatus.week_end_date == week_end_date)
    )
    return result.scalar_one_or_none()


async def was_weekly_report_sent(session: AsyncSession, week_end_date: date) -> bool:
    """Была ли уже отправлена недельная аналитика за эту неделю."""
    status = await get_status_by_week_end(session, week_end_date)
    return bool(status and status.is_sent)


async def mark_weekly_report_sent(session: AsyncSession, week_end_date: date) -> WeeklyReportStatus:
    """Отметить, что недельная аналитика за неделю отправлена."""
    status = await get_status_by_week_end(session, week_end_date)
    if status:
        status.is_sent = True
        session.add(status)
        await session.flush()
        await session.refresh(status)
        return status
    status = WeeklyReportStatus(week_end_date=week_end_date, is_sent=True)
    session.add(status)
    await session.flush()
    await session.refresh(status)
    return status
