"""
Обработчики продавца: открыть смену, моя смена, закрыть смену.
"""
from __future__ import annotations

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb_seller_main, kb_choose_shop
from bot.keyboards.common import kb_cancel
from bot.keyboards.seller import kb_after_shift_opened, kb_edit_report_after_submit
from bot.states.report import EditReportFSM
from bot.store import OPEN_SHIFT_BY_TELEGRAM
from repositories import shop_repo, shift_repo
from services import shift_service, report_service
from services.shift_service import ShiftError

router = Router()
logger = logging.getLogger(__name__)


def _get_cached_shift(telegram_id: int, seller_id: int) -> Optional[dict]:
    """Если в кэше есть открытая смена этого продавца — вернуть данные, иначе None."""
    data = OPEN_SHIFT_BY_TELEGRAM.get(telegram_id)
    if data and data.get("seller_id") == seller_id:
        return data
    return None


@router.message(F.text == "✏️ Редактировать отчёт")
async def edit_report_start(message: Message, state: FSMContext, session, seller, role, **kwargs):
    """Открыть редактирование своего отчёта за сегодня (до 24:00)."""
    if role != "seller" or not seller:
        await message.answer("Сначала привяжите аккаунт через /start.")
        return
    shift = await shift_service.get_seller_closed_shift_today(session, seller.id)
    if not shift or not shift.report:
        await message.answer("Нет закрытого отчёта за сегодня для редактирования.")
        return
    if not shift_service.can_edit_report(shift):
        await message.answer(
            "Редактирование недоступно: после 24:00 дня смены менять отчёт нельзя."
        )
        return
    await state.set_state(EditReportFSM.choosing_field)
    await state.update_data(edit_report_id=shift.report.id, edit_shift_id=shift.id)
    text = report_service.format_report_for_edit(shift.report)
    history = await report_service.get_edit_history_text(session, shift.report.id)
    if history:
        text += "\n\n" + history
    await message.answer(text, reply_markup=kb_edit_report_after_submit())


@router.message(F.text == "📂 Открыть смену")
async def open_shift_start(message: Message, session, seller, role, **kwargs):
    """Показать список торговых точек для открытия смены."""
    if role != "seller" or not seller:
        await message.answer("Сначала привяжите аккаунт через /start.")
        return
    telegram_id = message.from_user.id
    cached = _get_cached_shift(telegram_id, seller.id)
    if cached:
        await message.answer(
            f"У вас уже открыта смена на точке «{cached['address']}». "
            "Закройте её перед открытием новой."
        )
        return
    current = await shift_service.get_current_shift(session, seller.id)
    if current:
        await message.answer(
            f"У вас уже открыта смена на точке «{current.shop.address}». "
            "Закройте её перед открытием новой."
        )
        return
    shops = await shift_service.get_shops_for_select(session)
    if not shops:
        await message.answer("Нет доступных торговых точек. Обратитесь к руководителю.")
        return
    await message.answer("Выберите торговую точку:", reply_markup=kb_choose_shop(shops))


@router.callback_query(F.data.startswith("open_shop_"))
async def cb_open_shop(callback: CallbackQuery, session, seller, role, **kwargs):
    """Открыть смену на выбранной точке."""
    if role != "seller" or not seller:
        await callback.answer("Сначала привяжите аккаунт через /start.", show_alert=True)
        return
    shop_id = int(callback.data.split("_")[-1])
    try:
        shift = await shift_service.open_shift(session, seller.id, shop_id)
        shift_id = shift.id
        shift_date_str = shift.shift_date.strftime("%d.%m.%Y")
        shift_shop_id = shift.shop_id
        open_time_str = shift.open_time.strftime("%H:%M") if shift.open_time else "—"
        await session.commit()
        shop = await shop_repo.get_shop_by_id(session, shift_shop_id)
        address = shop.address if shop else "—"
        telegram_id = callback.from_user.id
        OPEN_SHIFT_BY_TELEGRAM[telegram_id] = {
            "shift_id": shift_id,
            "seller_id": seller.id,
            "address": address,
            "date_str": shift_date_str,
            "open_time_str": open_time_str,
        }
        await callback.answer()
        await callback.message.edit_text(f"Точка выбрана: {address}")
        await callback.message.answer(
            f"✅ Смена открыта.\n\n"
            f"Точка: {address}\n"
            f"Дата: {shift_date_str}\n"
            f"Открыта в: {open_time_str}\n\n"
            "Дальше можно нажать кнопку ниже или использовать меню.",
            reply_markup=kb_after_shift_opened(shift_id),
        )
    except ShiftError as e:
        await callback.answer(e.message, show_alert=True)
        await callback.message.edit_text(f"❌ {e.message}")


@router.callback_query(F.data.startswith("my_shift_"))
async def cb_my_shift(callback: CallbackQuery, session, seller, role, **kwargs):
    """Кнопка «Моя смена» под сообщением — смена по shift_id из callback."""
    if role != "seller" or not seller:
        await callback.answer("Сначала привяжите аккаунт через /start.", show_alert=True)
        return
    shift_id = int(callback.data.split("_")[-1])
    shift = await shift_repo.get_shift_by_id(session, shift_id)
    if not shift or shift.seller_id != seller.id or shift.status != "open":
        await callback.answer("Смена не найдена или уже закрыта.", show_alert=True)
        return
    await callback.answer()
    open_time_str = shift.open_time.strftime("%H:%M") if shift.open_time else "—"
    await callback.message.answer(
        f"📋 Ваша текущая смена:\n"
        f"Точка: {shift.shop.address}\n"
        f"Дата: {shift.shift_date.strftime('%d.%m.%Y')}\n"
        f"Открыта в: {open_time_str}\n\n"
        "Чтобы закрыть смену, нажмите «Закрыть смену» (кнопкой ниже или в меню) и заполните отчёт."
    )


# Продуктовые магазины: ввод выручки по мясу и по магазину отдельно
GROCERY_SHOP_ADDRESSES = ("Казаки продуктовый", "Строитель продуктовый")


def _is_grocery_shop(shift) -> bool:
    return bool(shift.shop and shift.shop.address in GROCERY_SHOP_ADDRESSES)


@router.callback_query(F.data.startswith("close_shift_"))
async def cb_close_shift(callback: CallbackQuery, session, seller, role, state, **kwargs):
    """Кнопка «Закрыть смену» под сообщением — запуск FSM по shift_id из callback."""
    if role != "seller" or not seller:
        await callback.answer("Сначала привяжите аккаунт через /start.", show_alert=True)
        return
    shift_id = int(callback.data.split("_")[-1])
    shift = await shift_repo.get_shift_by_id(session, shift_id)
    if not shift or shift.seller_id != seller.id or shift.status != "open":
        await callback.answer("Смена не найдена или уже закрыта.", show_alert=True)
        return
    from bot.states.report import ReportFSM
    is_grocery = _is_grocery_shop(shift)
    await state.update_data(shift_id=shift_id, seller_id=seller.id, is_grocery_shop=is_grocery)
    await callback.answer()
    await state.set_state(ReportFSM.receipts)
    await callback.message.answer(
        "Введите приход (число):",
        reply_markup=kb_cancel(),
    )


@router.message(F.text == "📋 Моя смена")
async def my_shift(message: Message, session, seller, role, **kwargs):
    """Показать текущую открытую смену."""
    if role != "seller" or not seller:
        await message.answer("Сначала привяжите аккаунт через /start.")
        return
    telegram_id = message.from_user.id
    cached = _get_cached_shift(telegram_id, seller.id)
    if cached:
        await message.answer(
            f"📋 Ваша текущая смена:\n"
            f"Точка: {cached['address']}\n"
            f"Дата: {cached['date_str']}\n"
            f"Открыта в: {cached['open_time_str']}\n\n"
            "Чтобы закрыть смену, нажмите «Закрыть смену» и заполните отчёт."
        )
        return
    current = await shift_service.get_current_shift(session, seller.id)
    if not current:
        await message.answer("У вас нет открытой смены.")
        return
    await message.answer(
        f"📋 Ваша текущая смена:\n"
        f"Точка: {current.shop.address}\n"
        f"Дата: {current.shift_date.strftime('%d.%m.%Y')}\n"
        f"Открыта в: {current.open_time.strftime('%H:%M') if current.open_time else '—'}\n\n"
        "Чтобы закрыть смену, нажмите «Закрыть смену» и заполните отчёт."
    )


@router.message(F.text == "✅ Закрыть смену")
async def close_shift_start(message: Message, session, seller, role, state, **kwargs):
    """Начать процесс закрытия смены (запуск FSM)."""
    if role != "seller" or not seller:
        await message.answer("Сначала привяжите аккаунт через /start.")
        return
    telegram_id = message.from_user.id
    cached = _get_cached_shift(telegram_id, seller.id)
    if cached:
        from bot.states.report import ReportFSM
        # Для кэша нет shop в контексте — запрашиваем смену для проверки продуктовой точки
        current = await shift_service.get_current_shift(session, seller.id)
        is_grocery = _is_grocery_shop(current) if current else False
        await state.update_data(shift_id=cached["shift_id"], seller_id=seller.id, is_grocery_shop=is_grocery)
        await state.set_state(ReportFSM.receipts)
        await message.answer("Введите приход (число):", reply_markup=kb_cancel())
        return
    current = await shift_service.get_current_shift(session, seller.id)
    if not current:
        await message.answer("У вас нет открытой смены. Нечего закрывать.")
        return
    from bot.states.report import ReportFSM
    is_grocery = _is_grocery_shop(current)
    await state.update_data(shift_id=current.id, seller_id=seller.id, is_grocery_shop=is_grocery)
    await state.set_state(ReportFSM.receipts)
    await message.answer("Введите приход (число):", reply_markup=kb_cancel())
