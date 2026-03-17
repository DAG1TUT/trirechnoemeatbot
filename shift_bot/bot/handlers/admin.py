"""
Обработчики админа: активные смены, отчёты, история, незакрытые точки.
"""
from __future__ import annotations

import logging
from datetime import date, datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb_admin_main
from bot.keyboards.admin import (
    kb_seller_rating,
    kb_shop_rating,
    kb_delete_scope,
    kb_delete_choose_shop,
    kb_delete_choose_seller,
    kb_delete_confirm,
    kb_admin_sellers_menu,
    kb_admin_shops_menu,
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
    return "\n".join(lines)


@router.message(F.text == "👤 Продавцы")
async def admin_manage_sellers_menu(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.managing_sellers)
    text = await _format_sellers_list(session)
    await message.answer(
        text + "\n\nВыберите действие:",
        reply_markup=kb_admin_sellers_menu(),
    )


@router.message(AdminFSM.managing_sellers, F.text)
async def admin_manage_sellers_actions(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    text = (message.text or "").strip()
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Возврат в главное меню.", reply_markup=kb_admin_main())
        return
    if text == "➕ Добавить продавца":
        await state.set_state(AdminFSM.adding_seller_name)
        await message.answer("Введите ФИО нового продавца:")
        return
    if text == "✏️ Переименовать продавца":
        sellers = await seller_repo.get_all_sellers(session)
        if not sellers:
            await message.answer("Список продавцов пуст.")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{s.id}. {s.full_name[:30]}",
                    callback_data=f"admin_seller_rename_{s.id}",
                )
            ]
            for s in sellers
        ]
        buttons.append(
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_seller_cancel")]
        )
        await state.set_state(AdminFSM.renaming_seller_choose)
        await message.answer(
            "Выберите продавца, которого нужно переименовать:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return
    if text == "🚫 Отключить продавца":
        sellers = [s for s in await seller_repo.get_all_sellers(session) if s.is_active]
        if not sellers:
            await message.answer("Нет активных продавцов.")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{s.id}. {s.full_name[:30]}",
                    callback_data=f"admin_seller_deactivate_{s.id}",
                )
            ]
            for s in sellers
        ]
        buttons.append(
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_seller_cancel")]
        )
        await message.answer(
            "Выберите продавца, которого нужно отключить:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return
    if text == "✅ Включить продавца":
        sellers = [s for s in await seller_repo.get_all_sellers(session) if not s.is_active]
        if not sellers:
            await message.answer("Нет отключённых продавцов.")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{s.id}. {s.full_name[:30]}",
                    callback_data=f"admin_seller_activate_{s.id}",
                )
            ]
            for s in sellers
        ]
        buttons.append(
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_seller_cancel")]
        )
        await message.answer(
            "Выберите продавца, которого нужно включить:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return


@router.message(AdminFSM.adding_seller_name, F.text)
async def admin_add_seller_name(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer("Имя не может быть пустым. Введите ФИО продавца:")
        return
    await seller_repo.create_seller(session, full_name)
    await state.set_state(AdminFSM.managing_sellers)
    text = await _format_sellers_list(session)
    await message.answer(
        "✅ Продавец добавлен.\n\n" + text,
        reply_markup=kb_admin_sellers_menu(),
    )


@router.callback_query(AdminFSM.renaming_seller_choose, F.data.startswith("admin_seller_rename_"))
async def admin_rename_seller_choose(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        seller_id = int(callback.data.replace("admin_seller_rename_", ""))
    except ValueError:
        await callback.answer()
        return
    await state.update_data(renaming_seller_id=seller_id)
    await state.set_state(AdminFSM.renaming_seller_new_name)
    await callback.answer()
    await callback.message.edit_text("Введите новое ФИО для выбранного продавца:")


@router.callback_query(F.data.startswith("admin_seller_deactivate_"))
async def admin_deactivate_seller(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        seller_id = int(callback.data.replace("admin_seller_deactivate_", ""))
    except ValueError:
        await callback.answer()
        return
    seller = await seller_repo.set_seller_active(session, seller_id, False)
    await callback.answer()
    if not seller:
        await callback.message.edit_text("❌ Продавец с таким id не найден.")
        return
    text = await _format_sellers_list(session)
    await callback.message.edit_text(
        f"✅ Продавец {seller.full_name} отключён.\n\n" + text
    )


@router.callback_query(F.data.startswith("admin_seller_activate_"))
async def admin_activate_seller(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        seller_id = int(callback.data.replace("admin_seller_activate_", ""))
    except ValueError:
        await callback.answer()
        return
    seller = await seller_repo.set_seller_active(session, seller_id, True)
    await callback.answer()
    if not seller:
        await callback.message.edit_text("❌ Продавец с таким id не найден.")
        return
    text = await _format_sellers_list(session)
    await callback.message.edit_text(
        f"✅ Продавец {seller.full_name} активирован.\n\n" + text
    )


@router.callback_query(F.data == "admin_seller_cancel")
async def admin_seller_cancel(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    await state.set_state(AdminFSM.managing_sellers)
    text = await _format_sellers_list(session)
    await callback.message.edit_text(
        text + "\n\nВыберите действие:",
    )
    await callback.answer()


@router.message(AdminFSM.renaming_seller_new_name, F.text)
async def admin_rename_seller_new_name(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    data = await state.get_data()
    seller_id = data.get("renaming_seller_id")
    new_name = (message.text or "").strip()
    if not seller_id:
        await state.set_state(AdminFSM.managing_sellers)
        await message.answer("Сессия сброшена. Начните заново.", reply_markup=kb_admin_sellers_menu())
        return
    if not new_name:
        await message.answer("Имя не может быть пустым. Введите новое ФИО продавца:")
        return
    seller = await seller_repo.update_seller_name(session, seller_id, new_name)
    await state.set_state(AdminFSM.managing_sellers)
    if not seller:
        await message.answer("❌ Продавец с таким id не найден.", reply_markup=kb_admin_sellers_menu())
        return
    text = await _format_sellers_list(session)
    await message.answer(
        f"✅ Имя продавца обновлено: {seller.full_name}.\n\n" + text,
        reply_markup=kb_admin_sellers_menu(),
    )


async def _format_shops_list(session) -> str:
    shops = await shop_repo.get_all_shops(session)
    if not shops:
        return "Список торговых точек пуст."
    lines: list[str] = ["🏬 Список торговых точек:\n"]
    for s in shops:
        status = "✅ активна" if s.is_active else "🚫 отключена"
        lines.append(f"{s.id}. {s.address} — {status}")
    return "\n".join(lines)


@router.message(F.text == "🏬 Торговые точки")
async def admin_manage_shops_menu(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    await state.set_state(AdminFSM.managing_shops)
    text = await _format_shops_list(session)
    await message.answer(
        text + "\n\nВыберите действие:",
        reply_markup=kb_admin_shops_menu(),
    )


@router.message(AdminFSM.managing_shops, F.text)
async def admin_manage_shops_actions(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    text = (message.text or "").strip()
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Возврат в главное меню.", reply_markup=kb_admin_main())
        return
    if text == "➕ Добавить точку":
        await state.set_state(AdminFSM.adding_shop_address)
        await message.answer("Введите адрес новой торговой точки:")
        return
    if text == "✏️ Переименовать точку":
        shops = await shop_repo.get_all_shops(session)
        if not shops:
            await message.answer("Список торговых точек пуст.")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{s.id}. {s.address[:30]}",
                    callback_data=f"admin_shop_rename_{s.id}",
                )
            ]
            for s in shops
        ]
        buttons.append(
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_shop_cancel")]
        )
        await state.set_state(AdminFSM.renaming_shop_choose)
        await message.answer(
            "Выберите точку, которую нужно переименовать:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return
    if text == "🚫 Отключить точку":
        shops = [s for s in await shop_repo.get_all_shops(session) if s.is_active]
        if not shops:
            await message.answer("Нет активных торговых точек.")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{s.id}. {s.address[:30]}",
                    callback_data=f"admin_shop_deactivate_{s.id}",
                )
            ]
            for s in shops
        ]
        buttons.append(
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_shop_cancel")]
        )
        await message.answer(
            "Выберите точку, которую нужно отключить:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return
    if text == "✅ Включить точку":
        shops = [s for s in await shop_repo.get_all_shops(session) if not s.is_active]
        if not shops:
            await message.answer("Нет отключённых торговых точек.")
            return
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{s.id}. {s.address[:30]}",
                    callback_data=f"admin_shop_activate_{s.id}",
                )
            ]
            for s in shops
        ]
        buttons.append(
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_shop_cancel")]
        )
        await message.answer(
            "Выберите точку, которую нужно включить:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return


@router.message(AdminFSM.adding_shop_address, F.text)
async def admin_add_shop_address(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    address = (message.text or "").strip()
    if not address:
        await message.answer("Адрес не может быть пустым. Введите адрес новой точки:")
        return
    await shop_repo.create_shop(session, address)
    await state.set_state(AdminFSM.managing_shops)
    text = await _format_shops_list(session)
    await message.answer(
        "✅ Торговая точка добавлена.\n\n" + text,
        reply_markup=kb_admin_shops_menu(),
    )


@router.callback_query(AdminFSM.renaming_shop_choose, F.data.startswith("admin_shop_rename_"))
async def admin_rename_shop_choose(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        shop_id = int(callback.data.replace("admin_shop_rename_", ""))
    except ValueError:
        await callback.answer()
        return
    await state.update_data(renaming_shop_id=shop_id)
    await state.set_state(AdminFSM.renaming_shop_new_address)
    await callback.answer()
    await callback.message.edit_text("Введите новый адрес для выбранной точки:")


@router.callback_query(F.data.startswith("admin_shop_deactivate_"))
async def admin_deactivate_shop(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        shop_id = int(callback.data.replace("admin_shop_deactivate_", ""))
    except ValueError:
        await callback.answer()
        return
    shop = await shop_repo.set_shop_active(session, shop_id, False)
    await callback.answer()
    if not shop:
        await callback.message.edit_text("❌ Точка с таким id не найдена.")
        return
    text = await _format_shops_list(session)
    await callback.message.edit_text(
        f"✅ Точка «{shop.address}» отключена.\n\n" + text
    )


@router.callback_query(F.data.startswith("admin_shop_activate_"))
async def admin_activate_shop(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    try:
        shop_id = int(callback.data.replace("admin_shop_activate_", ""))
    except ValueError:
        await callback.answer()
        return
    shop = await shop_repo.set_shop_active(session, shop_id, True)
    await callback.answer()
    if not shop:
        await callback.message.edit_text("❌ Точка с таким id не найдена.")
        return
    text = await _format_shops_list(session)
    await callback.message.edit_text(
        f"✅ Точка «{shop.address}» активирована.\n\n" + text
    )


@router.callback_query(F.data == "admin_shop_cancel")
async def admin_shop_cancel(callback: CallbackQuery, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        await callback.answer()
        return
    await state.set_state(AdminFSM.managing_shops)
    text = await _format_shops_list(session)
    await callback.message.edit_text(
        text + "\n\nВыберите действие:",
    )
    await callback.answer()


@router.message(AdminFSM.renaming_shop_new_address, F.text)
async def admin_rename_shop_new_address(message: Message, state: FSMContext, session, role, **kwargs):
    if not _admin_only(role):
        return
    data = await state.get_data()
    shop_id = data.get("renaming_shop_id")
    new_address = (message.text or "").strip()
    if not shop_id:
        await state.set_state(AdminFSM.managing_shops)
        await message.answer("Сессия сброшена. Начните заново.", reply_markup=kb_admin_shops_menu())
        return
    if not new_address:
        await message.answer("Адрес не может быть пустым. Введите новый адрес точки:")
        return
    shop = await shop_repo.update_shop_address(session, shop_id, new_address)
    await state.set_state(AdminFSM.managing_shops)
    if not shop:
        await message.answer("❌ Точка с таким id не найдена.", reply_markup=kb_admin_shops_menu())
        return
    text = await _format_shops_list(session)
    await message.answer(
        f"✅ Адрес точки обновлён: {shop.address}.\n\n" + text,
        reply_markup=kb_admin_shops_menu(),
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