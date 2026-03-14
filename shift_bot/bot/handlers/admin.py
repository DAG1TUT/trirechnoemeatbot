"""
Обработчики админа: активные смены, отчёты, история, незакрытые точки.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb_admin_main
from bot.store import LOGGED_OUT_ADMIN_IDS
from services import shift_service, report_service, reminder_service
from repositories import admin_repo
from config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)


def _admin_only(role: str) -> bool:
    return role == "admin"


def _parse_date(text: str) -> date | None:
    try:
        return datetime.strptime(text.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


@router.message(F.text == "🟢 Активные смены")
async def admin_active_shifts(message: Message, session, role, **kwargs):
    if not _admin_only(role):
        return
    shifts = await shift_service.get_active_shifts(session, for_date=date.today())
    if not shifts:
        await message.answer("Сейчас нет активных смен за сегодня.")
        return
    lines = ["🟢 Активные смены за сегодня:\n"]
    for s in shifts:
        lines.append(f"• {s.seller.full_name} — {s.shop.address} (открыта в {s.open_time.strftime('%H:%M') if s.open_time else '—'})")
    await message.answer("\n".join(lines))


@router.message(F.text == "👥 Кто где работает")
async def admin_who_where(message: Message, session, role, **kwargs):
    if not _admin_only(role):
        return
    shifts = await shift_service.get_active_shifts(session, for_date=date.today())
    if not shifts:
        await message.answer("Сейчас нет открытых смен. Никто не привязан к точкам.")
        return
    lines = ["👥 Кто где работает (сейчас):\n"]
    for s in shifts:
        lines.append(f"📍 {s.shop.address}\n   👤 {s.seller.full_name}")
    await message.answer("\n".join(lines))


@router.message(F.text == "📊 Отчет за сегодня")
async def admin_report_today(message: Message, session, role, **kwargs):
    """Промежуточный отчёт за сегодня (по закрытым сменам на момент запроса)."""
    if not _admin_only(role):
        return
    today = date.today()
    text = await report_service.get_daily_report_text(session, today)
    await message.answer("📊 Отчёт за сегодня (по закрытым сменам):\n\n" + text)


@router.message(F.text == "📄 Итоговый отчет")
async def admin_final_report(message: Message, session, role, **kwargs):
    """Ручное формирование итогового отчёта за сегодня. Отправляется в чат."""
    if not _admin_only(role):
        return
    today = date.today()
    text = await report_service.get_daily_report_text(session, today)
    await message.answer("📄 Итоговый отчёт за сегодня:\n\n" + text)


@router.message(F.text == "⚠️ Незакрытые точки")
async def admin_unclosed(message: Message, session, role, **kwargs):
    """Список точек, по которым сегодня ещё не закрыта смена."""
    if not _admin_only(role):
        return
    unclosed = await reminder_service.get_unclosed_shops_today(session)
    if not unclosed:
        await message.answer("✅ Все точки на сегодня закрыты.")
        return
    lines = ["⚠️ Торговые точки без закрытой смены за сегодня:\n"]
    for shop in unclosed:
        lines.append(f"• {shop.address}")
    await message.answer("\n".join(lines))


@router.message(F.text == "🚪 Выйти из режима администратора")
async def admin_logout(message: Message, session, role, telegram_id, **kwargs):
    """Выход из режима администратора: убрать из БД и помечать как вышедшего."""
    if not _admin_only(role):
        return
    await admin_repo.remove_admin_by_telegram_id(session, telegram_id)
    LOGGED_OUT_ADMIN_IDS.add(telegram_id)
    await message.answer(
        "Вы вышли из режима администратора.\n\nНажмите /start для выбора роли (продавец или войти снова как руководитель)."
    )


from bot.states.admin import AdminFSM


@router.message(F.text == "📅 История")
async def admin_history_start(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.waiting_report_date)
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ (например 13.03.2025):")


@router.message(AdminFSM.waiting_report_date, F.text)
async def admin_history_date(message: Message, state: FSMContext, session, role, **kwargs):
    """Обработка введённой даты для истории."""
    if not _admin_only(role):
        return
    d = _parse_date(message.text)
    await state.clear()
    if not d:
        await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
        return
    text = await report_service.get_daily_report_text(session, d)
    await message.answer(f"📅 Отчёт за {d.strftime('%d.%m.%Y')}:\n\n" + text)