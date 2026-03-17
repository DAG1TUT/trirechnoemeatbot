from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from fastapi import Depends, FastAPI, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.models.shift import Shift
from core.models.shift_report import ShiftReport
from core.models.shop import Shop
from repositories import shop_repo, seller_repo


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

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "day": target_date,
            "cards": cards,
            "total_revenue": total_revenue,
            "shops_total": len(shops),
            "shops_open": open_count,
            "shops_closed": closed_count,
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

