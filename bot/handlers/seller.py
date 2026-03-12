"""
Обработчики продавца: открыть смену, моя смена, закрыть смену.
"""
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.keyboards import kb_seller_main, kb_choose_shop
from bot.keyboards.common import kb_cancel
from services import shift_service
from services.shift_service import ShiftError

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📂 Открыть смену")
async def open_shift_start(message: Message, session, seller, role, **kwargs):
    """Показать список торговых точек для открытия смены."""
    if role != "seller" or not seller:
        await message.answer("Сначала привяжите аккаунт через /start.")
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
        await callback.answer("Смена открыта", show_alert=True)
        await callback.message.edit_text(
            f"✅ Смена открыта.\nТочка: {shift.shop.address}\nДата: {shift.shift_date.strftime('%d.%m.%Y')}"
        )
    except ShiftError as e:
        await callback.answer(e.message, show_alert=True)
        await callback.message.edit_text(f"❌ {e.message}")


@router.message(F.text == "📋 Моя смена")
async def my_shift(message: Message, session, seller, role, **kwargs):
    """Показать текущую открытую смену."""
    if role != "seller" or not seller:
        await message.answer("Сначала привяжите аккаунт через /start.")
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
    current = await shift_service.get_current_shift(session, seller.id)
    if not current:
        await message.answer("У вас нет открытой смены. Нечего закрывать.")
        return
    from bot.states.report import ReportFSM
    await state.update_data(shift_id=current.id, seller_id=seller.id)
    await state.set_state(ReportFSM.revenue)
    await message.answer(
        "Введите выручку за день (число):",
        reply_markup=kb_cancel(),
    )
