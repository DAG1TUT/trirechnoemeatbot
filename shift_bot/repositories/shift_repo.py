"""
Репозиторий смен.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, time

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.shift import Shift
from core.models.shift_report import ShiftReport


async def get_open_shift_by_seller_id(session: AsyncSession, seller_id: int) -> Shift | None:
    """Открытая смена продавца (не более одной), с загрузкой shop и seller."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
        )
        .where(Shift.seller_id == seller_id, Shift.status == "open")
        .order_by(Shift.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_open_shift_by_shop_id(session: AsyncSession, shop_id: int) -> Shift | None:
    """Открытая смена по точке (точка занята, если есть)."""
    result = await session.execute(
        select(Shift).where(Shift.shop_id == shop_id, Shift.status == "open")
    )
    return result.scalar_one_or_none()


async def get_shift_by_id(session: AsyncSession, shift_id: int) -> Shift | None:
    """Смена по id с загрузкой связей."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(Shift.id == shift_id)
    )
    return result.scalar_one_or_none()


async def get_all_open_shifts(session: AsyncSession, shift_date: date | None = None) -> list[Shift]:
    """Все открытые смены, опционально за дату."""
    q = select(Shift).where(Shift.status == "open")
    if shift_date is not None:
        q = q.where(Shift.shift_date == shift_date)
    q = q.options(
        selectinload(Shift.seller),
        selectinload(Shift.shop),
    ).order_by(Shift.shift_date, Shift.open_time)
    result = await session.execute(q)
    return list(result.scalars().all())


async def get_closed_shifts_by_date(
    session: AsyncSession, report_date: date
) -> list[Shift]:
    """Все закрытые смены за дату с отчётами и связями."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(Shift.shift_date == report_date, Shift.status == "closed")
        .order_by(Shift.close_time)
    )
    return list(result.scalars().all())


async def get_all_closed_shifts_with_report(session: AsyncSession) -> list[Shift]:
    """Все закрытые смены с отчётами и связями (для рейтингов)."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(Shift.status == "closed")
        .order_by(Shift.shift_date.desc(), Shift.close_time.desc())
    )
    return list(result.scalars().all())


async def get_closed_shifts_by_seller(
    session: AsyncSession, seller_id: int
) -> list[Shift]:
    """Все закрытые смены продавца с отчётами (для детализации по продавцу)."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(Shift.seller_id == seller_id, Shift.status == "closed")
        .order_by(Shift.shift_date.desc(), Shift.close_time.desc())
    )
    return list(result.scalars().all())


async def get_closed_shifts_by_shop(
    session: AsyncSession, shop_id: int
) -> list[Shift]:
    """Все закрытые смены по точке с отчётами (для детализации по точке)."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(Shift.shop_id == shop_id, Shift.status == "closed")
        .order_by(Shift.shift_date.desc(), Shift.close_time.desc())
    )
    return list(result.scalars().all())


async def get_shop_avg_revenue_before(
    session: AsyncSession,
    shop_id: int,
    before_date: date,
    days: int = 14,
) -> float | None:
    """
    Средняя выручка по точке за закрытые смены в период [before_date - days, before_date).
    Нужна для сравнения: если сегодняшняя выручка сильно ниже — пометка в отчёте.
    """
    start = before_date - timedelta(days=days)
    result = await session.execute(
        select(func.avg(ShiftReport.revenue))
        .select_from(Shift)
        .join(ShiftReport, Shift.id == ShiftReport.shift_id)
        .where(
            Shift.shop_id == shop_id,
            Shift.status == "closed",
            Shift.shift_date >= start,
            Shift.shift_date < before_date,
        )
    )
    scalar = result.scalar_one_or_none()
    if scalar is None:
        return None
    try:
        return float(scalar)
    except (TypeError, ValueError):
        return None


async def get_closed_shift_by_seller_and_date(
    session: AsyncSession, seller_id: int, shift_date: date
) -> Shift | None:
    """Закрытая смена продавца за указанную дату (для редактирования отчёта)."""
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(
            Shift.seller_id == seller_id,
            Shift.shift_date == shift_date,
            Shift.status == "closed",
        )
        .order_by(Shift.close_time.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_shift(
    session: AsyncSession,
    seller_id: int,
    shop_id: int,
    shift_date: date,
    open_time: time | None = None,
) -> Shift:
    """Создать открытую смену."""
    shift = Shift(
        seller_id=seller_id,
        shop_id=shop_id,
        shift_date=shift_date,
        open_time=open_time,
        status="open",
    )
    session.add(shift)
    await session.flush()
    await session.refresh(shift)
    return shift


async def close_shift(session: AsyncSession, shift_id: int, close_time: time | None = None) -> Shift | None:
    """Закрыть смену."""
    shift = await get_shift_by_id(session, shift_id)
    if not shift or shift.status != "open":
        return None
    shift.close_time = close_time or datetime.now().time()
    shift.status = "closed"
    session.add(shift)
    await session.flush()
    await session.refresh(shift)
    return shift
