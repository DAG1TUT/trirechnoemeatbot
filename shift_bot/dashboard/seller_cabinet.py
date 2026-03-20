"""
Веб-кабинет продавца: регистрация по ФИО из списка, вход, выход, отвязка веб-учётки,
открытие смены, закрытие с отчётом (как в Telegram-боте).
Префикс маршрутов: /seller-cabinet
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.models.shop import Shop
from core.models.seller import Seller
from repositories import seller_repo
from services import shift_service
from services.shift_service import ShiftError
from shift_bot.dashboard.password_util import hash_password, verify_password
from shift_bot.dashboard.seller_shift_notify import maybe_send_daily_final_and_weekly_reports

logger = logging.getLogger(__name__)

# Как в bot/handlers/seller.py — продуктовые точки: отчёт с мясом/магазином.
GROCERY_SHOP_ADDRESSES = ("Казаки продуктовый", "Строитель продуктовый")

router = APIRouter(prefix="/seller-cabinet", tags=["seller-cabinet"])

templates = Jinja2Templates(directory="shift_bot/dashboard/templates")

SESSION_KEY = "seller_id"


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def _parse_float(text: str) -> float | None:
    """Как в bot/handlers/report_fsm.py — пробелы, запятая как разделитель."""
    try:
        s = (text or "").replace(" ", "").replace("\u00a0", "").replace(",", ".").strip()
        if not s:
            return None
        return float(s)
    except ValueError:
        return None


def _is_grocery_shop(shop_address: str | None) -> bool:
    return bool(shop_address and shop_address in GROCERY_SHOP_ADDRESSES)


async def get_seller_from_session(request: Request, session: AsyncSession) -> Seller | None:
    sid = request.session.get(SESSION_KEY)
    if not sid:
        return None
    try:
        seller_id = int(sid)
    except (TypeError, ValueError):
        return None
    return await seller_repo.get_seller_by_id(session, seller_id)


@router.get("/", response_class=HTMLResponse)
async def seller_cabinet_root(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    seller = await get_seller_from_session(request, session)
    if not seller:
        return _redirect("/seller-cabinet/login")
    return _redirect("/seller-cabinet/home")


@router.get("/login", response_class=HTMLResponse)
async def seller_login_page(request: Request):
    return templates.TemplateResponse(
        "seller_cabinet_login.html",
        {"request": request, "error": None},
    )


@router.post("/login")
async def seller_login(
    request: Request,
    session: AsyncSession = Depends(get_session),
    seller_id: int = Form(...),
    password: str = Form(...),
):
    seller = await seller_repo.get_seller_by_id(session, seller_id)
    if (
        not seller
        or not seller.is_active
        or not seller.web_password_hash
        or not verify_password(password, seller.web_password_hash)
    ):
        return templates.TemplateResponse(
            "seller_cabinet_login.html",
            {
                "request": request,
                "error": "Неверный номер продавца или пароль.",
            },
            status_code=400,
        )
    request.session[SESSION_KEY] = seller.id
    return _redirect("/seller-cabinet/home")


@router.get("/register", response_class=HTMLResponse)
async def seller_register_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    available = await seller_repo.get_sellers_available_for_web_registration(session)
    return templates.TemplateResponse(
        "seller_cabinet_register.html",
        {
            "request": request,
            "sellers": available,
            "error": None,
        },
    )


@router.post("/register")
async def seller_register(
    request: Request,
    session: AsyncSession = Depends(get_session),
    seller_id: int = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    if password != password_confirm:
        available = await seller_repo.get_sellers_available_for_web_registration(session)
        return templates.TemplateResponse(
            "seller_cabinet_register.html",
            {
                "request": request,
                "sellers": available,
                "error": "Пароли не совпадают.",
            },
            status_code=400,
        )
    if len(password) < 6:
        available = await seller_repo.get_sellers_available_for_web_registration(session)
        return templates.TemplateResponse(
            "seller_cabinet_register.html",
            {
                "request": request,
                "sellers": available,
                "error": "Пароль не короче 6 символов.",
            },
            status_code=400,
        )

    seller = await seller_repo.get_seller_by_id(session, seller_id)
    if (
        not seller
        or not seller.is_active
        or (seller.web_password_hash and seller.web_password_hash.strip())
    ):
        available = await seller_repo.get_sellers_available_for_web_registration(session)
        return templates.TemplateResponse(
            "seller_cabinet_register.html",
            {
                "request": request,
                "sellers": available,
                "error": "Этот продавец недоступен для регистрации.",
            },
            status_code=400,
        )

    await seller_repo.set_web_password_hash(session, seller_id, hash_password(password))
    request.session[SESSION_KEY] = seller_id
    return _redirect("/seller-cabinet/home")


@router.get("/home", response_class=HTMLResponse)
async def seller_home(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    seller = await get_seller_from_session(request, session)
    if not seller:
        return _redirect("/seller-cabinet/login")
    flash = request.session.pop("flash", None)
    err = request.session.pop("error", None)
    current_shift = await shift_service.get_current_shift(session, seller.id)
    shops: list[Shop] = []
    if not current_shift:
        shops = await shift_service.get_shops_for_select(session)
    return templates.TemplateResponse(
        "seller_cabinet_home.html",
        {
            "request": request,
            "seller": seller,
            "current_shift": current_shift,
            "shops": shops,
            "flash": flash,
            "error": err,
        },
    )


@router.post("/shift/open")
async def seller_shift_open(
    request: Request,
    session: AsyncSession = Depends(get_session),
    shop_id: int = Form(...),
):
    seller = await get_seller_from_session(request, session)
    if not seller:
        return _redirect("/seller-cabinet/login")
    try:
        await shift_service.open_shift(session, seller.id, shop_id)
    except ShiftError as e:
        request.session["error"] = e.message
        return _redirect("/seller-cabinet/home")
    request.session["flash"] = "Смена открыта."
    return _redirect("/seller-cabinet/home")


@router.get("/shift/close", response_class=HTMLResponse)
async def seller_shift_close_get(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    seller = await get_seller_from_session(request, session)
    if not seller:
        return _redirect("/seller-cabinet/login")
    current = await shift_service.get_current_shift(session, seller.id)
    if not current or not current.shop:
        request.session["error"] = "Нет открытой смены."
        return _redirect("/seller-cabinet/home")
    is_grocery = _is_grocery_shop(current.shop.address)
    return templates.TemplateResponse(
        "seller_cabinet_close_shift.html",
        {
            "request": request,
            "seller": seller,
            "shift": current,
            "is_grocery": is_grocery,
            "error": None,
        },
    )


@router.post("/shift/close")
async def seller_shift_close_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
    shift_id: int = Form(...),
    receipts: str = Form("0"),
    revenue_meat: str = Form(""),
    revenue_store: str = Form(""),
    terminal_revenue: str = Form("0"),
    cash_revenue: str = Form("0"),
    cash_balance: str = Form(...),
    stock_balance: str = Form(...),
    expenses: str = Form(...),
    surrender_amount: str = Form("0"),
    comment: str = Form(""),
):
    seller = await get_seller_from_session(request, session)
    if not seller:
        return _redirect("/seller-cabinet/login")
    current = await shift_service.get_current_shift(session, seller.id)
    if not current or current.id != shift_id or not current.shop:
        request.session["error"] = "Смена не найдена или уже закрыта."
        return _redirect("/seller-cabinet/home")
    is_grocery = _is_grocery_shop(current.shop.address)

    r_receipts = _parse_float(receipts)
    if r_receipts is None:
        r_receipts = 0.0
    r_terminal = _parse_float(terminal_revenue)
    r_cash_rev = _parse_float(cash_revenue)
    r_cash_bal = _parse_float(cash_balance)
    r_stock = _parse_float(stock_balance)
    r_exp = _parse_float(expenses)
    r_surr = _parse_float(surrender_amount)
    if r_surr is None:
        r_surr = 0.0
    r_meat = _parse_float(revenue_meat) if (revenue_meat or "").strip() else None
    r_store = _parse_float(revenue_store) if (revenue_store or "").strip() else None

    def _close_error(msg: str):
        return templates.TemplateResponse(
            "seller_cabinet_close_shift.html",
            {
                "request": request,
                "seller": seller,
                "shift": current,
                "is_grocery": is_grocery,
                "error": msg,
            },
            status_code=400,
        )

    if None in (r_terminal, r_cash_rev, r_cash_bal, r_stock, r_exp):
        return _close_error("Введите числа во всех обязательных полях (можно 0).")

    nums = [r_receipts, r_terminal, r_cash_rev, r_cash_bal, r_stock, r_exp, r_surr]
    if is_grocery and (r_meat is None or r_store is None):
        return _close_error("Для продуктовой точки укажите выручку по мясу и по магазину.")
    if is_grocery:
        nums.extend([r_meat, r_store])
    if any(x is not None and x < 0 for x in nums):
        return _close_error("Значения не могут быть отрицательными.")

    if is_grocery:
        assert r_meat is not None and r_store is not None
        revenue_total = r_meat + r_store
        revenue_meat_v = r_meat
        revenue_store_v = r_store
    else:
        revenue_total = r_terminal + r_cash_rev
        revenue_meat_v = None
        revenue_store_v = None

    ok = await shift_service.save_shift_report(
        session,
        shift_id=shift_id,
        seller_id=seller.id,
        revenue=revenue_total,
        cash_balance=r_cash_bal,
        stock_balance=r_stock,
        expenses=r_exp,
        comment=(comment.strip() or "—"),
        revenue_meat=revenue_meat_v,
        revenue_store=revenue_store_v,
        terminal_revenue=r_terminal,
        cash_revenue=r_cash_rev,
        receipts=r_receipts,
        surrender_amount=r_surr,
    )
    if not ok:
        request.session["error"] = "Не удалось сохранить отчёт. Возможно, смена уже закрыта."
        return _redirect("/seller-cabinet/home")
    try:
        await maybe_send_daily_final_and_weekly_reports(session)
    except Exception:
        logger.exception("notify after web shift close")
    request.session["flash"] = "Смена закрыта, отчёт сохранён."
    return _redirect("/seller-cabinet/home")


@router.post("/logout")
async def seller_logout(request: Request):
    request.session.clear()
    return _redirect("/seller-cabinet/login")


@router.post("/unbind")
async def seller_unbind(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Сбросить веб-пароль: можно снова зарегистрироваться по ФИО из списка."""
    seller = await get_seller_from_session(request, session)
    if not seller:
        return _redirect("/seller-cabinet/login")
    await seller_repo.clear_web_password(session, seller.id)
    request.session.clear()
    return _redirect("/seller-cabinet/login")
