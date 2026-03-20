"""
Веб-кабинет продавца: регистрация по ФИО из списка, вход, выход, отвязка веб-учётки.
Префикс маршрутов: /seller-cabinet
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.models.seller import Seller
from repositories import seller_repo
from shift_bot.dashboard.password_util import hash_password, verify_password

router = APIRouter(prefix="/seller-cabinet", tags=["seller-cabinet"])

templates = Jinja2Templates(directory="shift_bot/dashboard/templates")

SESSION_KEY = "seller_id"


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


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
    return templates.TemplateResponse(
        "seller_cabinet_home.html",
        {
            "request": request,
            "seller": seller,
        },
    )


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
