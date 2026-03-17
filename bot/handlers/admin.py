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
from services import shift_service, report_service, reminder_service
from repositories import admin_repo, seller_repo, shop_repo
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


async def _format_sellers_list(session) -> str:
    sellers = await seller_repo.get_all_sellers(session)
    if not sellers:
        return "Список продавцов пуст."
    lines: list[str] = ["👤 Список продавцов:\n"]
    for s in sellers:
        status = "✅ активен" if s.is_active else "🚫 отключен"
        tg = f" (@{s.telegram_id})" if s.telegram_id else ""
        lines.append(f"{s.id}. {s.full_name}{tg} — {status}")
    lines.append(
        "\nКоманды управления продавцами:\n"
        "• `+Имя` — добавить продавца (пример: `+Иван Иванов`)\n"
        "• `id Новое имя` — переименовать (пример: `3 Пётр Петров`)\n"
        "• `-id` — отключить продавца (пример: `-2`)\n"
        "• `+id` — снова включить продавца (пример: `+2`)\n"
        "Напишите /start, чтобы выйти в главное меню."
    )
    return "\n".join(lines)


@router.message(F.text == "👤 Продавцы")
async def admin_manage_sellers_menu(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.managing_sellers)
    text = await _format_sellers_list(session)
    await message.answer(text)


@router.message(AdminFSM.managing_sellers, F.text)
async def admin_manage_sellers_input(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    text = message.text.strip()
    if text.lower() in {"/start", "выход", "назад"}:
        await state.clear()
        await message.answer(
            "Возврат в главное меню.",
            reply_markup=kb_admin_main(),
        )
        return

    # Добавление нового продавца: +Имя
    if text.startswith("+") and " " not in text[1:]:
        # Это может быть команда активации по id (+id), обработаем ниже
        pass
    if text.startswith("+") and " " in text[1:]:
        full_name = text[1:].strip()
        if not full_name:
            await message.answer("Укажите имя после '+', пример: `+Иван Иванов`.")
        else:
            await seller_repo.create_seller(session, full_name)
            await message.answer("✅ Продавец добавлен.")
        await message.answer(await _format_sellers_list(session))
        return

    # Отключение/включение продавца: -id или +id
    if (text.startswith("-") or text.startswith("+")) and text[1:].strip().isdigit():
        seller_id = int(text[1:].strip())
        is_active = text.startswith("+")
        seller = await seller_repo.set_seller_active(session, seller_id, is_active)
        if not seller:
            await message.answer("❌ Продавец с таким id не найден.")
        else:
            status = "активирован" if is_active else "отключён"
            await message.answer(f"✅ Продавец {seller.full_name} {status}.")
        await message.answer(await _format_sellers_list(session))
        return

    # Переименование: id Новое имя
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        seller_id = int(parts[0])
        new_name = parts[1].strip()
        seller = await seller_repo.update_seller_name(session, seller_id, new_name)
        if not seller:
            await message.answer("❌ Продавец с таким id не найден.")
        else:
            await message.answer(f"✅ Имя продавца обновлено: {seller.full_name}.")
        await message.answer(await _format_sellers_list(session))
        return

    await message.answer(
        "Не удалось распознать команду.\n"
        "Используйте один из форматов:\n"
        "• `+Имя` — добавить продавца\n"
        "• `id Новое имя` — переименовать\n"
        "• `-id` — отключить продавца\n"
        "• `+id` — включить продавца\n"
        "Или напишите /start для выхода."
    )


async def _format_shops_list(session) -> str:
    shops = await shop_repo.get_all_shops(session)
    if not shops:
        return "Список торговых точек пуст."
    lines: list[str] = ["🏬 Список торговых точек:\n"]
    for s in shops:
        status = "✅ активна" if s.is_active else "🚫 отключена"
        lines.append(f"{s.id}. {s.address} — {status}")
    lines.append(
        "\nКоманды управления точками:\n"
        "• `+Адрес` — добавить точку (пример: `+ул. Новая, д. 1`)\n"
        "• `id Новый адрес` — переименовать (пример: `2 ул. Пушкина, д. 5`)\n"
        "• `-id` — отключить точку (пример: `-3`)\n"
        "• `+id` — снова включить точку (пример: `+3`)\n"
        "Напишите /start, чтобы выйти в главное меню."
    )
    return "\n".join(lines)


@router.message(F.text == "🏬 Торговые точки")
async def admin_manage_shops_menu(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.managing_shops)
    text = await _format_shops_list(session)
    await message.answer(text)


@router.message(AdminFSM.managing_shops, F.text)
async def admin_manage_shops_input(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    text = message.text.strip()
    if text.lower() in {"/start", "выход", "назад"}:
        await state.clear()
        await message.answer(
            "Возврат в главное меню.",
            reply_markup=kb_admin_main(),
        )
        return

    # Добавление новой точки: +Адрес (если после + есть пробел)
    if text.startswith("+") and " " in text[1:]:
        address = text[1:].strip()
        if not address:
            await message.answer("Укажите адрес после '+', пример: `+ул. Новая, д. 1`.")
        else:
            await shop_repo.create_shop(session, address)
            await message.answer("✅ Торговая точка добавлена.")
        await message.answer(await _format_shops_list(session))
        return

    # Отключение/включение точки: -id или +id
    if (text.startswith("-") or text.startswith("+")) and text[1:].strip().isdigit():
        shop_id = int(text[1:].strip())
        is_active = text.startswith("+")
        shop = await shop_repo.set_shop_active(session, shop_id, is_active)
        if not shop:
            await message.answer("❌ Точка с таким id не найдена.")
        else:
            status = "активирована" if is_active else "отключена"
            await message.answer(f"✅ Точка «{shop.address}» {status}.")
        await message.answer(await _format_shops_list(session))
        return

    # Переименование: id Новый адрес
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        shop_id = int(parts[0])
        new_address = parts[1].strip()
        shop = await shop_repo.update_shop_address(session, shop_id, new_address)
        if not shop:
            await message.answer("❌ Точка с таким id не найдена.")
        else:
            await message.answer(f"✅ Адрес точки обновлён: {shop.address}.")
        await message.answer(await _format_shops_list(session))
        return

    await message.answer(
        "Не удалось распознать команду.\n"
        "Используйте один из форматов:\n"
        "• `+Адрес` — добавить точку\n"
        "• `id Новый адрес` — переименовать\n"
        "• `-id` — отключить точку\n"
        "• `+id` — включить точку\n"
        "Или напишите /start для выхода."
    )