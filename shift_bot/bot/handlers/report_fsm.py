"""
FSM: пошаговый ввод отчёта при закрытии смены.
"""
from __future__ import annotations

import logging
from datetime import date

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.common import kb_cancel, kb_cancel_back, kb_confirm_big_value
from bot.keyboards.seller import (
    kb_confirm_close_shift,
    kb_edit_report_field,
    kb_edit_report_after_submit,
    kb_edit_report_offer,
)
from bot.states.report import ReportFSM, EditReportFSM
from bot.store import OPEN_SHIFT_BY_TELEGRAM
from services import shift_service, report_service
from repositories import admin_repo, shift_repo, shift_report_repo, shop_repo

router = Router()
logger = logging.getLogger(__name__)

# Пороги для переспроса «точно ли такое большое значение?» (по полям отчёта)
BIG_VALUE_THRESHOLDS = {
    "revenue": 200_000,
    "cash_balance": 150_000,
    "stock_balance": 150_000,
    "expenses": 50_000,
}
# Куда переходить после поля (для основного потока)
_NEXT_STATE_AFTER_FIELD = {
    "revenue": ReportFSM.cash_balance,
    "cash_balance": ReportFSM.stock_balance,
    "stock_balance": ReportFSM.expenses,
    "expenses": ReportFSM.comment,
}
_PROMPT_AFTER_FIELD = {
    "revenue": "Введите остаток наличных (число):",
    "cash_balance": "Введите остаток товара (число или количество):",
    "stock_balance": "Введите расходы / списания (число):",
    "expenses": "Введите комментарий (можно кратко или «—»):",
}
_FIRST_PROMPT = {
    "revenue": "Введите выручку за день (число):",
    "cash_balance": "Введите остаток наличных (число):",
    "stock_balance": "Введите остаток товара (число или количество):",
    "expenses": "Введите расходы / списания (число):",
}


def _parse_float(text: str) -> float | None:
    """Парсит число: допускает пробелы (25 000), запятую как дробный разделитель."""
    try:
        s = (text or "").replace(" ", "").replace("\u00a0", "").replace(",", ".").strip()
        if not s:
            return None
        return float(s)
    except ValueError:
        return None


def _format_summary(data: dict) -> str:
    """Текст итогового отчёта для подтверждения."""
    return (
        "Проверьте данные:\n"
        f"💰 Выручка: {data['revenue']:,.2f}\n"
        f"💵 Остаток наличных: {data['cash_balance']:,.2f}\n"
        f"📦 Остаток товара: {data['stock_balance']:,.2f}\n"
        f"📉 Расходы: {data['expenses']:,.2f}\n"
        f"💬 Комментарий: {data.get('comment', '—')}\n\n"
        "Подтвердите закрытие смены:"
    )


async def _ask_confirm_big_value(
    message: Message, state: FSMContext, field: str, val: float, from_editing: bool = False
) -> None:
    """Переспросить при подозрительно большом значении."""
    await state.update_data(
        pending_field=field,
        pending_value=val,
        pending_from_editing=from_editing,
    )
    await state.set_state(ReportFSM.confirm_big_value)
    await message.answer(
        f"Вы ввели {val:,.0f}. Это очень большое значение.\n\n"
        "Подтвердите: точно так и должно быть?",
        reply_markup=kb_confirm_big_value(),
    )


@router.message(ReportFSM.revenue, F.text)
async def step_revenue(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (выручка), например 15000.50")
        return
    if val >= BIG_VALUE_THRESHOLDS.get("revenue", float("inf")):
        await _ask_confirm_big_value(message, state, "revenue", val, from_editing=False)
        return
    await state.update_data(revenue=val)
    await state.set_state(ReportFSM.cash_balance)
    await message.answer("Введите остаток наличных (число):", reply_markup=kb_cancel_back())


@router.message(ReportFSM.cash_balance, F.text)
async def step_cash_balance(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (остаток наличных), например 5000")
        return
    if val >= BIG_VALUE_THRESHOLDS.get("cash_balance", float("inf")):
        await _ask_confirm_big_value(message, state, "cash_balance", val, from_editing=False)
        return
    await state.update_data(cash_balance=val)
    await state.set_state(ReportFSM.stock_balance)
    await message.answer("Введите остаток товара (число или количество):", reply_markup=kb_cancel_back())


@router.message(ReportFSM.stock_balance, F.text)
async def step_stock_balance(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (остаток товара)")
        return
    if val >= BIG_VALUE_THRESHOLDS.get("stock_balance", float("inf")):
        await _ask_confirm_big_value(message, state, "stock_balance", val, from_editing=False)
        return
    await state.update_data(stock_balance=val)
    await state.set_state(ReportFSM.expenses)
    await message.answer("Введите расходы / списания (число):", reply_markup=kb_cancel_back())


@router.message(ReportFSM.expenses, F.text)
async def step_expenses(message: Message, state: FSMContext, session, **kwargs):
    val = _parse_float(message.text)
    if val is None or val < 0:
        await message.answer("Введите число (расходы), например 200")
        return
    if val >= BIG_VALUE_THRESHOLDS.get("expenses", float("inf")):
        await _ask_confirm_big_value(message, state, "expenses", val, from_editing=False)
        return
    await state.update_data(expenses=val)
    await state.set_state(ReportFSM.comment)
    await message.answer("Введите комментарий (можно кратко или «—»):", reply_markup=kb_cancel_back())


@router.message(ReportFSM.comment, F.text)
async def step_comment(message: Message, state: FSMContext, session, **kwargs):
    await state.update_data(comment=message.text.strip() or "—")
    await state.set_state(ReportFSM.confirm)
    data = await state.get_data()
    await message.answer(_format_summary(data), reply_markup=kb_confirm_close_shift())


# Возврат на предыдущий шаг ввода отчёта: (текущее состояние, куда перейти, текст, клавиатура)
_BACK_STEPS = [
    (ReportFSM.cash_balance, ReportFSM.revenue, "Введите выручку за день (число):", kb_cancel),
    (ReportFSM.stock_balance, ReportFSM.cash_balance, "Введите остаток наличных (число):", kb_cancel_back),
    (ReportFSM.expenses, ReportFSM.stock_balance, "Введите остаток товара (число или количество):", kb_cancel_back),
    (ReportFSM.comment, ReportFSM.expenses, "Введите расходы / списания (число):", kb_cancel_back),
]


@router.callback_query(F.data == "report_step_back")
async def report_step_back(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Кнопка «Назад» — вернуться к предыдущему полю отчёта."""
    current = await state.get_state()
    if not current:
        await callback.answer()
        return
    for from_state, to_state, prompt, kb in _BACK_STEPS:
        if from_state.state == current:
            await state.set_state(to_state)
            await callback.answer("Назад")
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.answer(prompt, reply_markup=kb())
            return
    await callback.answer()


@router.callback_query(ReportFSM.confirm_big_value, F.data == "report_confirm_big_yes")
async def report_confirm_big_yes(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Подтвердили большое значение — сохраняем и переходим к следующему шагу или к итогу."""
    data = await state.get_data()
    field = data.get("pending_field")
    value = data.get("pending_value")
    from_editing = data.get("pending_from_editing", False)
    updates = {
        field: value,
        "pending_field": None,
        "pending_value": None,
        "pending_from_editing": None,
    }
    if from_editing:
        updates["edit_field"] = None
    await state.update_data(**updates)
    await callback.answer("Принято")
    if from_editing:
        await state.set_state(ReportFSM.confirm)
        new_data = await state.get_data()
        await callback.message.edit_text(
            _format_summary(new_data),
            reply_markup=kb_confirm_close_shift(),
        )
        return
    next_state = _NEXT_STATE_AFTER_FIELD.get(field)
    prompt = _PROMPT_AFTER_FIELD.get(field, "")
    await state.set_state(next_state)
    await callback.message.edit_text(prompt, reply_markup=kb_cancel_back())


@router.callback_query(ReportFSM.confirm_big_value, F.data == "report_confirm_big_no")
async def report_confirm_big_no(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отказ — вводим значение заново."""
    data = await state.get_data()
    field = data.get("pending_field")
    from_editing = data.get("pending_from_editing", False)
    await state.update_data(
        pending_field=None, pending_value=None, pending_from_editing=None,
        edit_field=field if from_editing else None,
    )
    await callback.answer("Введите заново")
    if from_editing:
        await state.set_state(ReportFSM.editing)
        prompt = _EDIT_PROMPTS.get(field, "")
        await callback.message.edit_text(prompt, reply_markup=kb_cancel())
    else:
        await state.set_state(getattr(ReportFSM, field))
        prompt = _FIRST_PROMPT.get(field, "")
        await callback.message.edit_text(prompt, reply_markup=kb_cancel_back() if field != "revenue" else kb_cancel())


@router.callback_query(ReportFSM.confirm, F.data == "report_edit")
async def report_edit_start(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Показать выбор поля для изменения."""
    await callback.answer()
    await callback.message.edit_text("✏️ Что изменить?", reply_markup=kb_edit_report_field())


_EDIT_PROMPTS = {
    "revenue": "Введите новое значение выручки (число):",
    "cash_balance": "Введите новый остаток наличных (число):",
    "stock_balance": "Введите новый остаток товара (число):",
    "expenses": "Введите новые расходы (число):",
    "comment": "Введите новый комментарий (или «—»):",
}


@router.callback_query(ReportFSM.confirm, F.data.startswith("report_edit_"))
async def report_edit_choose(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Выбрано поле для изменения — запрашиваем новое значение."""
    data_name = callback.data.replace("report_edit_", "")
    if data_name == "back":
        data = await state.get_data()
        await callback.answer()
        await callback.message.edit_text(_format_summary(data), reply_markup=kb_confirm_close_shift())
        return
    field_map = {
        "revenue": "revenue",
        "cash": "cash_balance",
        "stock": "stock_balance",
        "expenses": "expenses",
        "comment": "comment",
    }
    edit_field = field_map.get(data_name)
    if not edit_field:
        await callback.answer()
        return
    await state.update_data(edit_field=edit_field)
    await state.set_state(ReportFSM.editing)
    await callback.answer()
    await callback.message.edit_text(
        _EDIT_PROMPTS[edit_field],
        reply_markup=kb_cancel(),
    )


@router.message(ReportFSM.editing, F.text)
async def report_edit_value(message: Message, state: FSMContext, **kwargs):
    """Принято новое значение при редактировании — обновляем данные и снова показываем итог."""
    data = await state.get_data()
    edit_field = data.get("edit_field")
    if not edit_field:
        await state.set_state(ReportFSM.confirm)
        return
    if edit_field == "comment":
        value = message.text.strip() or "—"
        await state.update_data(comment=value, edit_field=None)
    else:
        val = _parse_float(message.text)
        if val is None or val < 0:
            await message.answer(f"Введите число. {_EDIT_PROMPTS[edit_field]}")
            return
        if val >= BIG_VALUE_THRESHOLDS.get(edit_field, float("inf")):
            await _ask_confirm_big_value(message, state, edit_field, val, from_editing=True)
            return
        await state.update_data(**{edit_field: val}, edit_field=None)
    await state.set_state(ReportFSM.confirm)
    new_data = await state.get_data()
    await message.answer(_format_summary(new_data), reply_markup=kb_confirm_close_shift())


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
    # Кнопка «Редактировать отчёт» только в тот же день (до 24:00)
    await callback.message.answer(
        "До конца дня можно изменить данные отчёта:",
        reply_markup=kb_edit_report_offer(shift_id),
    )

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

            # Воскресенье: отправить недельную аналитику один раз за неделю
            if today.weekday() == 6:  # 6 = воскресенье
                if not await report_service.was_weekly_report_sent(session, today):
                    weekly_text = await report_service.get_weekly_analytics_text(session, today)
                    for aid in admin_ids:
                        try:
                            await callback.bot.send_message(
                                aid,
                                "📬 Недельная аналитика (все точки закрыты в воскресенье):\n\n" + weekly_text,
                            )
                        except Exception as e:
                            logger.exception("Send weekly report to admin %s: %s", aid, e)
                    await report_service.mark_weekly_report_sent(session, today)


@router.callback_query(ReportFSM.editing, F.data == "report_cancel")
async def report_edit_cancel(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отмена редактирования — вернуться к итогу отчёта."""
    await state.update_data(edit_field=None)
    await state.set_state(ReportFSM.confirm)
    data = await state.get_data()
    await callback.answer("Отменено")
    await callback.message.edit_text(_format_summary(data), reply_markup=kb_confirm_close_shift())


@router.callback_query(EditReportFSM.waiting_value, F.data == "report_cancel")
async def edit_report_value_cancel(callback: CallbackQuery, state: FSMContext, session, **kwargs):
    """Отмена ввода значения — вернуться к выбору поля."""
    await state.update_data(edit_field=None)
    await state.set_state(EditReportFSM.choosing_field)
    data = await state.get_data()
    report_id = data.get("edit_report_id")
    if report_id:
        report = await shift_report_repo.get_report_by_id(session, report_id)
        if report:
            text = report_service.format_report_for_edit(report)
            history = await report_service.get_edit_history_text(session, report_id)
            if history:
                text += "\n\n" + history
            await callback.message.edit_text(text, reply_markup=kb_edit_report_after_submit())
    await callback.answer("Отменено")


@router.callback_query(F.data == "report_cancel")
async def report_cancel(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отмена ввода отчёта."""
    await state.clear()
    await callback.answer("Отменено")
    await callback.message.edit_text("Ввод отчёта отменён. Смена остаётся открытой.")


# ----- Редактирование отчёта после отправки (до 24:00 того же дня) -----

_EDIT_AFTER_PROMPTS = {
    "revenue": "Введите новое значение выручки (число):",
    "cash_balance": "Введите новый остаток наличных (число):",
    "stock_balance": "Введите новый остаток товара (число):",
    "expenses": "Введите новые расходы (число):",
    "comment": "Введите новый комментарий (или «—»):",
}

_EDIT_FIELD_MAP = {
    "revenue": "revenue",
    "cash": "cash_balance",
    "stock": "stock_balance",
    "expenses": "expenses",
    "comment": "comment",
}


@router.callback_query(F.data.startswith("edit_report_offer_"))
async def edit_report_offer(callback: CallbackQuery, state: FSMContext, session, seller, role, **kwargs):
    """Открыть экран редактирования отчёта (проверка: свой отчёт, тот же день)."""
    if role != "seller" or not seller:
        await callback.answer("Ошибка: привяжите аккаунт через /start.", show_alert=True)
        return
    try:
        shift_id = int(callback.data.replace("edit_report_offer_", ""))
    except ValueError:
        await callback.answer()
        return
    shift = await shift_repo.get_shift_by_id(session, shift_id)
    if not shift or shift.seller_id != seller.id or not shift.report:
        await callback.answer("Отчёт не найден.", show_alert=True)
        return
    if not shift_service.can_edit_report(shift):
        await callback.answer(
            "Редактирование недоступно: после 24:00 дня смены менять отчёт нельзя.",
            show_alert=True,
        )
        return
    await state.set_state(EditReportFSM.choosing_field)
    await state.update_data(edit_report_id=shift.report.id, edit_shift_id=shift_id)
    text = report_service.format_report_for_edit(shift.report)
    history = await report_service.get_edit_history_text(session, shift.report.id)
    if history:
        text += "\n\n" + history
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=kb_edit_report_after_submit())


@router.callback_query(EditReportFSM.choosing_field, F.data.startswith("edit_report_field_"))
async def edit_report_choose_field(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Выбрано поле для изменения — запрашиваем новое значение."""
    name = callback.data.replace("edit_report_field_", "")
    edit_field = _EDIT_FIELD_MAP.get(name)
    if not edit_field:
        await callback.answer()
        return
    await state.update_data(edit_field=edit_field)
    await state.set_state(EditReportFSM.waiting_value)
    await callback.answer()
    await callback.message.edit_text(
        _EDIT_AFTER_PROMPTS[edit_field],
        reply_markup=kb_cancel(),
    )


@router.callback_query(EditReportFSM.choosing_field, F.data == "edit_report_done")
async def edit_report_done(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Завершить редактирование отчёта."""
    await state.clear()
    await callback.answer("Готово")
    await callback.message.edit_text("✅ Редактирование отчёта завершено.")


@router.message(EditReportFSM.waiting_value, F.text)
async def edit_report_value_entered(message: Message, state: FSMContext, session, seller, role, **kwargs):
    """Введено новое значение при редактировании отправленного отчёта."""
    if role != "seller" or not seller:
        await state.clear()
        return
    data = await state.get_data()
    report_id = data.get("edit_report_id")
    edit_field = data.get("edit_field")
    if not report_id or not edit_field:
        await state.set_state(EditReportFSM.choosing_field)
        return
    if edit_field == "comment":
        value = message.text.strip() or "—"
        kw = {edit_field: value}
    else:
        val = _parse_float(message.text)
        if val is None or val < 0:
            await message.answer(f"Введите число. {_EDIT_AFTER_PROMPTS[edit_field]}")
            return
        kw = {edit_field: val}
    ok = await shift_service.update_shift_report_with_log(
        session,
        report_id=report_id,
        seller_id=seller.id,
        telegram_id=message.from_user.id,
        full_name=(message.from_user.full_name or "").strip() or "Продавец",
        **kw,
    )
    if not ok:
        await message.answer("Не удалось обновить отчёт.")
        return
    await state.update_data(edit_field=None)
    await state.set_state(EditReportFSM.choosing_field)
    report = await shift_report_repo.get_report_by_id(session, report_id)
    text = "✅ Изменено.\n\n" + report_service.format_report_for_edit(report)
    history = await report_service.get_edit_history_text(session, report_id)
    if history:
        text += "\n\n" + history
    await message.answer(text, reply_markup=kb_edit_report_after_submit())