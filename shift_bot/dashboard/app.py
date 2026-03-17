from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_session
from core.models.shift import Shift
from core.models.shift_report import ShiftReport
from core.models.shop import Shop
from repositories import shop_repo, seller_repo, shift_repo, daily_report_status_repo
from services import shift_service, report_service


app = FastAPI(title="Trirechno Meat Dashboard")

app.mount("/static", StaticFiles(directory="shift_bot/dashboard/static"), name="static")
templates = Jinja2Templates(directory="shift_bot/dashboard/templates")


def _parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


async def _get_unclosed_shops_for_date(session: AsyncSession, target_date: date) -> list[Shop]:
    """
    Торговые точки, по которым за указанную дату ещё нет закрытой смены.
    Аналог reminder_service.get_unclosed_shops_today, но с произвольной датой.
    """
    all_shops = await shop_repo.get_all_active_shops(session)
    all_ids = {s.id for s in all_shops}
    result = await session.execute(
        select(Shift.shop_id)
        .where(
            Shift.shift_date == target_date,
            Shift.status == "closed",
        )
        .distinct()
    )
    closed_ids = set(result.scalars().all())
    unclosed_ids = all_ids - closed_ids
    return [s for s in all_shops if s.id in unclosed_ids]


@app.get("/", response_class=HTMLResponse)
async def dashboard_index(
    request: Request,
    session: AsyncSession = Depends(get_session),
    day: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD"),
):
    target_date = _parse_date(day)

    shops_result = await session.execute(select(Shop).order_by(Shop.id))
    shops: list[Shop] = list(shops_result.scalars().all())

    open_shifts_subq = (
        select(Shift.shop_id)
        .where(Shift.shift_date == target_date, Shift.status == "open")
        .subquery()
    )

    revenue_result = await session.execute(
        select(Shift.shop_id, func.coalesce(func.sum(ShiftReport.revenue), 0.0))
        .join(ShiftReport, ShiftReport.shift_id == Shift.id)
        .where(
            Shift.shift_date == target_date,
            Shift.status == "closed",
        )
        .group_by(Shift.shop_id)
    )
    revenue_by_shop: dict[int, float] = {row[0]: float(row[1]) for row in revenue_result.all()}

    shifts_count_result = await session.execute(
        select(Shift.shop_id, func.count(Shift.id))
        .where(Shift.shift_date == target_date)
        .group_by(Shift.shop_id)
    )
    shifts_count_by_shop: dict[int, int] = {row[0]: int(row[1]) for row in shifts_count_result.all()}

    open_shop_ids_result = await session.execute(select(open_shifts_subq.c.shop_id))
    open_shop_ids = {row[0] for row in open_shop_ids_result.all()}

    cards = []
    total_revenue = 0.0
    open_count = 0

    for shop in shops:
        revenue = revenue_by_shop.get(shop.id, 0.0)
        shifts_count = shifts_count_by_shop.get(shop.id, 0)
        is_open = shop.id in open_shop_ids

        if revenue:
            total_revenue += revenue
        if is_open:
            open_count += 1

        cards.append(
            {
                "id": shop.id,
                "address": shop.address,
                "is_active": shop.is_active,
                "is_open": is_open,
                "revenue": revenue,
                "shifts_count": shifts_count,
            }
        )

    closed_count = len(shops) - open_count

    sellers = await seller_repo.get_all_sellers(session)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "day": target_date,
            "view": "dashboard",
            "cards": cards,
            "total_revenue": total_revenue,
            "shops_total": len(shops),
            "shops_open": open_count,
            "shops_closed": closed_count,
            "shops": shops,
            "sellers": sellers,
        },
    )


@app.get("/online", response_class=HTMLResponse)
async def dashboard_online(
    request: Request,
    session: AsyncSession = Depends(get_session),
    day: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD"),
):
    target_date = _parse_date(day)

    active_shifts = await shift_service.get_active_shifts(session, for_date=target_date)
    unclosed_shops = await _get_unclosed_shops_for_date(session, target_date)

    return templates.TemplateResponse(
        "online.html",
        {
            "request": request,
            "day": target_date,
            "view": "online",
            "active_shifts": active_shifts,
            "unclosed_shops": unclosed_shops,
            "active_count": len(active_shifts),
            "unclosed_count": len(unclosed_shops),
        },
    )


@app.get("/reports", response_class=HTMLResponse)
async def dashboard_reports(
    request: Request,
    session: AsyncSession = Depends(get_session),
    start: Optional[str] = Query(None, description="Начало периода YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="Конец периода YYYY-MM-DD"),
):
    start_date = _parse_date(start)
    end_date = _parse_date(end) if end else start_date
    if end_date < start_date:
        start_date, end_date = end_date, start_date

    result = await session.execute(
        select(
            Shift.shift_date,
            func.coalesce(func.sum(ShiftReport.revenue), 0.0),
            func.count(Shift.id),
        )
        .join(ShiftReport, ShiftReport.shift_id == Shift.id)
        .where(
            Shift.shift_date >= start_date,
            Shift.shift_date <= end_date,
            Shift.status == "closed",
        )
        .group_by(Shift.shift_date)
        .order_by(Shift.shift_date)
    )
    rows = result.all()

    daily = []
    total_revenue = 0.0
    total_shifts = 0
    for d, revenue, count in rows:
        revenue = float(revenue or 0.0)
        count = int(count or 0)
        daily.append(
            {
                "date": d,
                "revenue": revenue,
                "shifts_count": count,
            }
        )
        total_revenue += revenue
        total_shifts += count

    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
            "view": "reports",
            "start_date": start_date,
            "end_date": end_date,
            "daily": daily,
            "total_revenue": total_revenue,
            "total_shifts": total_shifts,
        },
    )


@app.get("/report/day", response_class=HTMLResponse)
async def dashboard_report_day(
    request: Request,
    session: AsyncSession = Depends(get_session),
    day: Optional[str] = Query(None, description="Дата YYYY-MM-DD"),
):
    """Детальный отчёт за один день (как в боте: по точкам выручка, остатки, комментарий)."""
    target_date = _parse_date(day)
    shifts = await shift_repo.get_closed_shifts_by_date(session, target_date)
    report_sent = await report_service.was_final_report_sent(session, target_date)
    status = await daily_report_status_repo.get_status_by_date(session, target_date)
    total_revenue = sum((s.report.revenue for s in shifts if s.report), 0.0)
    return templates.TemplateResponse(
        "report_day.html",
        {
            "request": request,
            "view": "reports",
            "day": target_date,
            "shifts": shifts,
            "report_sent": report_sent,
            "sent_at": status.sent_at if status else None,
            "total_revenue": total_revenue,
        },
    )


@app.post("/report/day/mark-sent")
async def dashboard_report_day_mark_sent(
    day: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    """Отметить итоговый отчёт за день как отправленный."""
    target_date = _parse_date(day)
    await report_service.mark_final_report_sent(session, target_date)
    return RedirectResponse(
        url=f"/report/day?day={target_date.strftime('%Y-%m-%d')}",
        status_code=303,
    )


@app.get("/shop/{shop_id:int}", response_class=HTMLResponse)
async def dashboard_shop_detail(
    request: Request,
    shop_id: int,
    session: AsyncSession = Depends(get_session),
    start: Optional[str] = Query(None, description="Начало периода YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="Конец периода YYYY-MM-DD"),
):
    """Статистика и все данные по датам для одной точки."""
    shop = await shop_repo.get_shop_by_id(session, shop_id)
    if not shop:
        return RedirectResponse(url="/", status_code=303)
    end_date = _parse_date(end)
    start_date = _parse_date(start)
    if not start:
        start_date = end_date - timedelta(days=89)
    if end_date < start_date:
        start_date, end_date = end_date, start_date
    # Запрос без зависимости от shift_repo.get_closed_shifts_in_date_range (его может не быть в корневом репо)
    result = await session.execute(
        select(Shift)
        .options(
            selectinload(Shift.seller),
            selectinload(Shift.shop),
            selectinload(Shift.report),
        )
        .where(
            Shift.shop_id == shop_id,
            Shift.status == "closed",
            Shift.shift_date >= start_date,
            Shift.shift_date <= end_date,
        )
        .order_by(Shift.shift_date.desc(), Shift.close_time.desc())
    )
    shop_shifts = list(result.scalars().all())
    by_date: dict[date, list] = {}
    for s in shop_shifts:
        d = s.shift_date
        if d not in by_date:
            by_date[d] = []
        by_date[d].append(s)
    rows = []
    total_revenue = 0.0
    for d in sorted(by_date.keys(), reverse=True):
        day_shifts = by_date[d]
        day_revenue = sum(
            (s.report.revenue for s in day_shifts if s.report),
            0.0,
        )
        sellers = ", ".join(
            (s.seller.full_name for s in day_shifts if s.seller)
        ) or "—"
        total_revenue += day_revenue
        rows.append(
            {
                "date": d,
                "revenue": day_revenue,
                "sellers": sellers,
                "shifts_count": len(day_shifts),
            }
        )
    return templates.TemplateResponse(
        "shop_detail.html",
        {
            "request": request,
            "shop": shop,
            "start_date": start_date,
            "end_date": end_date,
            "rows": rows,
            "total_revenue": total_revenue,
            "total_days": len(rows),
        },
    )


@app.get("/shops", response_class=HTMLResponse)
async def dashboard_shops(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    shops = await shop_repo.get_all_shops(session)
    return templates.TemplateResponse(
        "shops.html",
        {
            "request": request,
            "shops": shops,
        },
    )


@app.post("/shops/add")
async def dashboard_shops_add(
    address: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    address = (address or "").strip()
    if address:
        await shop_repo.create_shop(session, address)
    return RedirectResponse(url="/shops", status_code=303)


@app.post("/shops/rename")
async def dashboard_shops_rename(
    shop_id: int = Form(...),
    address: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    await shop_repo.update_shop_address(session, shop_id, address)
    return RedirectResponse(url="/shops", status_code=303)


@app.post("/shops/toggle")
async def dashboard_shops_toggle(
    shop_id: int = Form(...),
    is_active: bool = Form(...),
    session: AsyncSession = Depends(get_session),
):
    await shop_repo.set_shop_active(session, shop_id, is_active)
    return RedirectResponse(url="/shops", status_code=303)


@app.get("/sellers", response_class=HTMLResponse)
async def dashboard_sellers(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    sellers = await seller_repo.get_all_sellers(session)
    return templates.TemplateResponse(
        "sellers.html",
        {
            "request": request,
            "sellers": sellers,
        },
    )


@app.post("/sellers/add")
async def dashboard_sellers_add(
    full_name: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    full_name = (full_name or "").strip()
    if full_name:
        await seller_repo.create_seller(session, full_name)
    return RedirectResponse(url="/sellers", status_code=303)


@app.post("/sellers/rename")
async def dashboard_sellers_rename(
    seller_id: int = Form(...),
    full_name: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    await seller_repo.update_seller_name(session, seller_id, full_name)
    return RedirectResponse(url="/sellers", status_code=303)


@app.post("/sellers/toggle")
async def dashboard_sellers_toggle(
    seller_id: int = Form(...),
    is_active: bool = Form(...),
    session: AsyncSession = Depends(get_session),
):
    await seller_repo.set_seller_active(session, seller_id, is_active)
    return RedirectResponse(url="/sellers", status_code=303)


@app.post("/sellers/bind-telegram")
async def dashboard_sellers_bind_telegram(
    seller_id: int = Form(...),
    telegram_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
):
    """Привязать или отвязать Telegram ID у продавца. Пустое значение — отвязка."""
    seller = await seller_repo.get_seller_by_id(session, seller_id)
    if not seller:
        return RedirectResponse(url="/", status_code=303)
    raw = (telegram_id or "").strip()
    if not raw:
        seller.telegram_id = None
        session.add(seller)
        await session.flush()
    else:
        try:
            tid = int(raw)
            await seller_repo.bind_telegram_to_seller(session, seller_id, tid)
        except ValueError:
            pass
    return RedirectResponse(url="/sellers", status_code=303)

