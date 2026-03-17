"""
Обработчики админа: активные смены, отчёты, история, незакрытые точки.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb_admin_main
from bot.keyboards.admin import (
    kb_seller_rating,
    kb_shop_rating,
    kb_delete_scope,
    kb_delete_choose_shop,
    kb_delete_choose_seller,
    kb_delete_confirm,
)
from bot.store import LOGGED_OUT_ADMIN_IDS
from services import shift_service, report_service, reminder_service
from services import rating_service
from repositories import admin_repo, shift_repo, shop_repo, seller_repo
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


@router.message(F.text == "📈 Рейтинг продавцов")
async def admin_seller_rating(message: Message, session, role, **kwargs):
    """Рейтинг продавцов по средней выручке; кнопки — провал в детали по продавцу."""
    if not _admin_only(role):
        return
    rows = await rating_service.get_seller_rating(session)
    if not rows:
        await message.answer("Нет данных по закрытым сменам для рейтинга продавцов.")
        return
    lines = ["📈 Рейтинг продавцов (по средней выручке):\n"]
    for i, r in enumerate(rows, 1):
        name = r.seller.full_name or f"ID{r.seller.id}"
        lines.append(
            f"{i}. {name} — {r.avg_revenue:,.0f} ₽ (среднее), смен: {r.shifts_count}"
        )
    await message.answer(
        "\n".join(lines),
        reply_markup=kb_seller_rating(rows),
    )


@router.message(F.text == "📈 Рейтинг точек")
async def admin_shop_rating(message: Message, session, role, **kwargs):
    """Рейтинг точек по средней выручке; кнопки — провал в детали по точке."""
    if not _admin_only(role):
        return
    rows = await rating_service.get_shop_rating(session)
    if not rows:
        await message.answer("Нет данных по закрытым сменам для рейтинга точек.")
        return
    lines = ["📈 Рейтинг точек (по средней выручке):\n"]
    for i, r in enumerate(rows, 1):
        addr = r.shop.address or f"Точка {r.shop.id}"
        lines.append(
            f"{i}. {addr} — {r.avg_revenue:,.0f} ₽ (среднее), смен: {r.shifts_count}"
        )
    await message.answer(
        "\n".join(lines),
        reply_markup=kb_shop_rating(rows),
    )


@router.callback_query(F.data.startswith("seller_rating_"))
async def admin_seller_rating_drill(callback: CallbackQuery, session, role, **kwargs):
    """Провал в продавца: в какой день на какой точке, сколько сдал."""
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        seller_id = int(callback.data.replace("seller_rating_", ""))
    except ValueError:
        await callback.answer()
        return
    shifts = await rating_service.get_seller_shifts_detail(session, seller_id)
    if not shifts:
        await callback.answer("Нет смен у этого продавца.", show_alert=True)
        return
    seller_name = shifts[0].seller.full_name if shifts[0].seller else f"ID{seller_id}"
    lines = [f"👤 {seller_name}\nСмены (дата — точка — выручка):\n"]
    total = 0.0
    for s in shifts:
        rev = s.report.revenue if s.report else 0
        total += rev
        date_str = s.shift_date.strftime("%d.%m.%Y") if s.shift_date else "—"
        addr = s.shop.address if s.shop else f"Точка {s.shop_id}"
        lines.append(f"  • {date_str} — {addr} — {rev:,.0f} ₽")
    lines.append(f"\nВсего выручки за все смены: {total:,.0f} ₽")
    await callback.answer()
    await callback.message.answer("\n".join(lines))


@router.callback_query(F.data.startswith("shop_rating_"))
async def admin_shop_rating_drill(callback: CallbackQuery, session, role, **kwargs):
    """Провал в точку: кто в какой день работал и сколько сдал."""
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        shop_id = int(callback.data.replace("shop_rating_", ""))
    except ValueError:
        await callback.answer()
        return
    shifts = await rating_service.get_shop_shifts_detail(session, shop_id)
    if not shifts:
        await callback.answer("Нет смен по этой точке.", show_alert=True)
        return
    shop_addr = shifts[0].shop.address if shifts[0].shop else f"Точка {shop_id}"
    lines = [f"📍 {shop_addr}\nСмены (дата — кто работал — выручка):\n"]
    total = 0.0
    for s in shifts:
        rev = s.report.revenue if s.report else 0
        total += rev
        date_str = s.shift_date.strftime("%d.%m.%Y") if s.shift_date else "—"
        who = s.seller.full_name if s.seller else f"ID{s.seller_id}"
        lines.append(f"  • {date_str} — {who} — {rev:,.0f} ₽")
    lines.append(f"\nВсего выручки по точке за все смены: {total:,.0f} ₽")
    await callback.answer()
    await callback.message.answer("\n".join(lines))


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

    # Добавление нового продавца: +Имя (где после + есть пробел)
    if text.startswith("+") and " " in text[1:]:
        full_name = text[1:].strip()
        if not full_name:
            await message.answer("Укажите имя после '+', пример: `+Иван Иванов`.")
        else:
            await seller_repo.create_seller(session, full_name)
            await message.answer("✅ Продавец добавлен.")
        await message.answer(await _format_sellers_list(session))
        return

    # Отключение/включение продавца: -id или +id (без пробела)
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


def _parse_period(text: str) -> tuple[date | None, date | None]:
    """Парсит «ДД.ММ.ГГГГ - ДД.ММ.ГГГГ» или «ДД.ММ.ГГГГ-ДД.ММ.ГГГГ». Возвращает (start, end) или (None, None)."""
    s = (text or "").strip()
    if "-" not in s:
        return None, None
    parts = s.split("-", 1)
    if len(parts) != 2:
        return None, None
    start = _parse_date(parts[0].strip())
    end = _parse_date(parts[1].strip())
    return start, end


@router.message(F.text == "📁 Архив отчётов")
async def admin_archive_start(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.waiting_archive_period)
    await message.answer(
        "Введите период: дата начала и дата конца в формате\n"
        "ДД.ММ.ГГГГ - ДД.ММ.ГГГГ\n"
        "Например: 01.03.2025 - 07.03.2025"
    )


@router.message(AdminFSM.waiting_archive_period, F.text)
async def admin_archive_period(message: Message, state: FSMContext, session, role, **kwargs):
    """Обработка введённого периода для архива."""
    if not _admin_only(role):
        return
    start, end = _parse_period(message.text)
    await state.clear()
    if not start or not end:
        await message.answer(
            "Неверный формат. Введите период так: ДД.ММ.ГГГГ - ДД.ММ.ГГГГ\n"
            "Например: 01.03.2025 - 07.03.2025"
        )
        return
    if start > end:
        await message.answer("Дата начала не может быть позже даты конца. Введите период заново.")
        return
    text = await report_service.get_archive_report_text(session, start, end)
    # Telegram лимит 4096 символов на сообщение
    max_len = 4000
    if len(text) <= max_len:
        await message.answer(text)
    else:
        for i in range(0, len(text), max_len):
            chunk = text[i : i + max_len]
            await message.answer(chunk)


# ----- Удаление данных за дату (по дате / по точке / по продавцу) -----


@router.message(F.text == "🗑 Удалить данные за дату")
async def admin_delete_by_date_start(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.waiting_delete_date)
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ (смены и отчёты за эту дату можно будет удалить):")


@router.message(AdminFSM.waiting_delete_date, F.text)
async def admin_delete_date_entered(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    d = _parse_date(message.text)
    if not d:
        await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
        return
    await state.update_data(delete_date=d.isoformat())
    await state.set_state(None)
    shifts = await shift_repo.get_shifts_by_date(session, d)
    if not shifts:
        await message.answer(f"За {d.strftime('%d.%m.%Y')} нет смен. Нечего удалять.")
        return
    await message.answer(
        f"За {d.strftime('%d.%m.%Y')} найдено смен: {len(shifts)}.\nЧто удалить?",
        reply_markup=kb_delete_scope(),
    )


@router.callback_query(F.data == "delete_scope_all")
async def admin_delete_scope_all(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    data = await state.get_data()
    date_str = data.get("delete_date")
    if not date_str:
        await callback.answer("Сессия сброшена. Начните заново.", show_alert=True)
        await state.clear()
        return
    from datetime import date as date_type
    d = date_type.fromisoformat(date_str)
    shifts = await shift_repo.get_shifts_by_date(session, d)
    await state.update_data(delete_scope="all", delete_shop_id=None, delete_seller_id=None)
    await callback.message.edit_text(
        f"Удалить все смены за {d.strftime('%d.%m.%Y')}? (всего {len(shifts)} смен)",
        reply_markup=kb_delete_confirm(),
    )
    await callback.answer()


@router.callback_query(F.data == "delete_scope_shop")
async def admin_delete_scope_shop(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    shops = await shop_repo.get_all_active_shops(session)
    if not shops:
        await callback.answer("Нет точек.", show_alert=True)
        return
    await callback.message.edit_text("Выберите точку (удалятся смены за выбранную дату только по этой точке):", reply_markup=kb_delete_choose_shop(shops))
    await callback.answer()


@router.callback_query(F.data == "delete_scope_seller")
async def admin_delete_scope_seller(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    sellers = await seller_repo.get_all_active_sellers(session)
    if not sellers:
        await callback.answer("Нет продавцов.", show_alert=True)
        return
    await callback.message.edit_text("Выберите продавца (удалятся смены за выбранную дату только по этому продавцу):", reply_markup=kb_delete_choose_seller(sellers))
    await callback.answer()


@router.callback_query(F.data.startswith("delete_shop_"))
@router.callback_query(F.data.startswith("delete_seller_"))
async def admin_delete_scope_chosen(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    from datetime import date as date_type
    data = await state.get_data()
    date_str = data.get("delete_date")
    if not date_str:
        await callback.answer("Сессия сброшена.", show_alert=True)
        await state.clear()
        return
    d = date_type.fromisoformat(date_str)
    if callback.data.startswith("delete_shop_"):
        shop_id = int(callback.data.replace("delete_shop_", ""))
        shifts = await shift_repo.get_shifts_by_date(session, d, shop_id=shop_id)
        shop = await shop_repo.get_shop_by_id(session, shop_id)
        name = shop.address if shop else f"Точка {shop_id}"
        await state.update_data(delete_scope="shop", delete_shop_id=shop_id, delete_seller_id=None)
        await callback.message.edit_text(
            f"Удалить смены за {d.strftime('%d.%m.%Y')} по точке «{name}»? (смен: {len(shifts)})",
            reply_markup=kb_delete_confirm(),
        )
    else:
        seller_id = int(callback.data.replace("delete_seller_", ""))
        shifts = await shift_repo.get_shifts_by_date(session, d, seller_id=seller_id)
        from repositories import seller_repo as sr
        sellers = await sr.get_all_active_sellers(session)
        seller = next((s for s in sellers if s.id == seller_id), None)
        name = seller.full_name if seller else f"ID{seller_id}"
        await state.update_data(delete_scope="seller", delete_shop_id=None, delete_seller_id=seller_id)
        await callback.message.edit_text(
            f"Удалить смены за {d.strftime('%d.%m.%Y')} по продавцу «{name}»? (смен: {len(shifts)})",
            reply_markup=kb_delete_confirm(),
        )
    await callback.answer()


@router.callback_query(F.data == "delete_confirm_yes")
async def admin_delete_confirm_yes(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    from datetime import date as date_type
    data = await state.get_data()
    date_str = data.get("delete_date")
    if not date_str:
        await callback.answer("Сессия сброшена.", show_alert=True)
        await state.clear()
        return
    d = date_type.fromisoformat(date_str)
    scope = data.get("delete_scope")
    shop_id = data.get("delete_shop_id") if scope == "shop" else None
    seller_id = data.get("delete_seller_id") if scope == "seller" else None
    n = await shift_repo.delete_shifts_for_date(session, d, shop_id=shop_id, seller_id=seller_id)
    await state.clear()
    await callback.message.edit_text(f"✅ Удалено смен: {n}.")
    await callback.answer("Готово", show_alert=True)


@router.callback_query(F.data == "delete_cancel")
async def admin_delete_cancel(callback: CallbackQuery, state: FSMContext, **kwargs):
    await state.clear()
    await callback.message.edit_text("Удаление отменено.")
    await callback.answer()