"""
FSM: пошаговый ввод отчёта при закрытии смены.
"""
from __future__ import annotations

import logging
from datetime import date

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.common import kb_cancel
from bot.keyboards.seller import kb_confirm_close_shift
from bot.states.report import ReportFSM
from bot.store import OPEN_SHIFT_BY_TELEGRAM
from services import shift_service, report_service
from repositories import admin_repo, shift_repo, shop_repo

router = Router()
logger = logging.getLogger(__name__)


def _parse_float(text: str) -> float | None:
    try:
        s = text.replace(",", ".").strip()
        return float(s)
    except ValueError:
        return None


@router.message(ReportFSM.revenue, F.text)
async def step_revenue(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (выручка), например 15000.50")
        return
    await state.update_data(revenue=val)
    await state.set_state(ReportFSM.cash_balance)
    await message.answer("Введите остаток наличных (число):", reply_markup=kb_cancel())


@router.message(ReportFSM.cash_balance, F.text)
async def step_cash_balance(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (остаток наличных), например 5000")
        return
    await state.update_data(cash_balance=val)
    await state.set_state(ReportFSM.stock_balance)
    await message.answer("Введите остаток товара (число или количество):", reply_markup=kb_cancel())


@router.message(ReportFSM.stock_balance, F.text)
async def step_stock_balance(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (остаток товара)")
        return
    await state.update_data(stock_balance=val)
    await state.set_state(ReportFSM.expenses)
    await message.answer("Введите расходы / списания (число):", reply_markup=kb_cancel())


@router.message(ReportFSM.expenses, F.text)
async def step_expenses(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (расходы), например 200")
        return
    await state.update_data(expenses=val)
    await state.set_state(ReportFSM.comment)
    await message.answer("Введите комментарий (можно кратко или «—»):", reply_markup=kb_cancel())


@router.message(ReportFSM.comment, F.text)
async def step_comment(message: Message, state: FSMContext, session, **kwargs):
    await state.update_data(comment=message.text.strip() or "—")
    await state.set_state(ReportFSM.confirm)
    data = await state.get_data()
    summary = (
        "Проверьте данные:\n"
        f"💰 Выручка: {data['revenue']:,.2f}\n"
        f"💵 Остаток наличных: {data['cash_balance']:,.2f}\n"
        f"📦 Остаток товара: {data['stock_balance']:,.2f}\n"
        f"📉 Расходы: {data['expenses']:,.2f}\n"
        f"💬 Комментарий: {data.get('comment', '—')}\n\n"
        "Подтвердите закрытие смены:"
    )
    await message.answer(summary, reply_markup=kb_confirm_close_shift())


@router.callback_query(ReportFSM.confirm, F.data == "report_confirm")
async def report_confirm(callback: CallbackQuery, state: FSMContext, session, seller, role, **kwargs):
    """Подтверждение: сохранить отчёт и закрыть смену."""
    if role != "seller" or not seller:
        await callback.answer("Ошибка: привяжите аккаунт через /start.", show_alert=True)
        await state.clear()
        return
    data = await state.get_data()
    shift_id = data.get("shift_id")
    if not shift_id:
        await callback.answer("Ошибка: смена не найдена. Начните заново.", show_alert=True)
        await state.clear()
        return
    ok = await shift_service.save_shift_report(
        session,
        shift_id=shift_id,
        seller_id=seller.id,
        revenue=data["revenue"],
        cash_balance=data["cash_balance"],
        stock_balance=data["stock_balance"],
        expenses=data["expenses"],
        comment=data.get("comment", ""),
    )
    await state.clear()
    if not ok:
        await callback.answer("Не удалось закрыть смену. Возможно, она уже закрыта.", show_alert=True)
        await callback.message.edit_text("❌ Смена не была закрыта. Попробуйте «Моя смена» или откройте заново.")
        return
    OPEN_SHIFT_BY_TELEGRAM.pop(callback.from_user.id, None)
    await callback.answer("Смена закрыта", show_alert=True)
    await callback.message.edit_text("✅ Смена успешно закрыта. Отчёт сохранён.")

    # Проверка: все ли точки за день закрыты — отправить итоговый отчёт админам один раз
    today = date.today()
    closed = await shift_repo.get_closed_shifts_by_date(session, today)
    all_shops = await shop_repo.get_all_active_shops(session)
    closed_shop_ids = {s.shop_id for s in closed}
    all_shop_ids = {s.id for s in all_shops}
    if all_shop_ids and closed_shop_ids >= all_shop_ids:
        already_sent = await report_service.was_final_report_sent(session, today)
        if not already_sent:
            report_text = await report_service.get_daily_report_text(session, today)
            admin_ids = list(await admin_repo.get_all_admin_telegram_ids(session))
            from config import ADMIN_IDS
            for aid in ADMIN_IDS:
                if aid not in admin_ids:
                    admin_ids.append(aid)
            for aid in admin_ids:
                try:
                    await callback.bot.send_message(
                        aid,
                        "📬 Итоговый отчёт за день (все точки закрыты):\n\n" + report_text,
                    )
                except Exception as e:
                    logger.exception("Send final report to admin %s: %s", aid, e)
            await report_service.mark_final_report_sent(session, today)


@router.callback_query(F.data == "report_cancel")
async def report_cancel(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отмена ввода отчёта."""
    await state.clear()
    await callback.answer("Отменено")
    await callback.message.edit_text("Ввод отчёта отменён. Смена остаётся открытой.")