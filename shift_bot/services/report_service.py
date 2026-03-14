"""
Сервис отчётов: сборка текста итогового/промежуточного отчёта за день.
Архитектура готова к добавлению экспорта в Excel (отдельный модуль).
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shift import Shift
from core.models.shift_report_edit import ShiftReportEdit
from core.models.shop import Shop
from repositories import (
    daily_report_status_repo,
    shift_repo,
    shift_report_edit_repo,
    shop_repo,
    weekly_report_status_repo,
)

_FIELD_LABELS = {
    "revenue": "Выручка",
    "cash_balance": "Остаток наличных",
    "stock_balance": "Остаток товара",
    "expenses": "Расходы",
    "comment": "Комментарий",
}


def _format_one_edit(edit: ShiftReportEdit) -> str:
    """Одна строка истории: когда, кто, что изменил."""
    try:
        changes = json.loads(edit.changes)
    except Exception:
        changes = {}
    dt = edit.edited_at
    if isinstance(dt, datetime) and dt.tzinfo:
        dt = dt.replace(tzinfo=None)
    time_str = dt.strftime("%d.%m.%Y %H:%M") if isinstance(dt, datetime) else str(dt)
    who = edit.edited_by_name or f"id{edit.edited_by_telegram_id}"
    parts = [f"  {time_str} — {who}:"]
    for field, pair in changes.items():
        label = _FIELD_LABELS.get(field, field)
        old_v = pair.get("old", "")
        new_v = pair.get("new", "")
        if field == "comment":
            parts.append(f"    {label}: «{old_v}» → «{new_v}»")
        else:
            try:
                old_v = f"{float(old_v):,.2f}"
                new_v = f"{float(new_v):,.2f}"
            except (TypeError, ValueError):
                pass
            parts.append(f"    {label}: {old_v} → {new_v}")
    return "\n".join(parts)


def format_report_for_edit(report) -> str:
    """Текст текущих данных отчёта для экрана редактирования."""
    return (
        "Текущие данные отчёта:\n"
        f"💰 Выручка: {report.revenue:,.2f}\n"
        f"💵 Остаток наличных: {report.cash_balance:,.2f}\n"
        f"📦 Остаток товара: {report.stock_balance:,.2f}\n"
        f"📉 Расходы: {report.expenses:,.2f}\n"
        f"💬 Комментарий: {report.comment or '—'}\n\n"
        "Что изменить?"
    )


async def get_edit_history_text(session: AsyncSession, shift_report_id: int) -> str:
    """Текст блока «История изменений» по отчёту (пустая строка, если правок не было)."""
    edits = await shift_report_edit_repo.get_edits_by_report_id(session, shift_report_id)
    if not edits:
        return ""
    lines = ["📝 История изменений:"]
    for edit in edits:
        lines.append(_format_one_edit(edit))
    return "\n".join(lines)


# Порог: если выручка точки в этот день меньше 50% от средней за предыдущие дни — помечаем
LOW_REVENUE_RATIO = 0.5
# За сколько дней считаем среднюю выручку по точке (до даты отчёта)
AVG_REVENUE_DAYS = 14


def _format_shift_report(shift: Shift, low_revenue_warning: bool = False) -> str:
    """Форматирование одной смены для отчёта. low_revenue_warning — пометка «подозрительно низкая выручка»."""
    seller_name = shift.seller.full_name
    address = shift.shop.address
    if shift.report:
        r = shift.report
        revenue = r.revenue
        cash = r.cash_balance
        stock = r.stock_balance
        expenses = r.expenses
        comment = r.comment or "—"
    else:
        revenue = cash = stock = expenses = 0.0
        comment = "—"
    block = (
        f"📍 {address}\n"
        f"👤 {seller_name}\n"
        f"💰 Выручка: {revenue:,.2f}\n"
        f"💵 Остаток наличных: {cash:,.2f}\n"
        f"📦 Остаток товара: {stock:,.2f}\n"
        f"📉 Расходы/списания: {expenses:,.2f}\n"
        f"💬 Комментарий: {comment}\n"
    )
    if low_revenue_warning:
        block += "⚠️ Подозрительно низкая выручка (ниже обычной по этой точке)\n"
    return block


def build_daily_report_text(shifts: list[Shift], report_date: date) -> str:
    """
    Собрать единое сообщение отчёта за день.
    Внизу — итоги по всем позициям: выручка, остаток наличных, остаток товара, расходы.
    """
    if not shifts:
        return f"📅 Отчёт за {report_date.strftime('%d.%m.%Y')}\n\nНет данных по закрытым сменам."

    total_revenue = 0.0
    total_cash = 0.0
    total_stock = 0.0
    total_expenses = 0.0
    lines = [f"📅 Итоговый отчёт за {report_date.strftime('%d.%m.%Y')}\n"]
    for shift in shifts:
        lines.append(_format_shift_report(shift))
        if shift.report:
            r = shift.report
            total_revenue += r.revenue
            total_cash += r.cash_balance
            total_stock += r.stock_balance
            total_expenses += r.expenses
    lines.append(
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 ИТОГО выручка: {total_revenue:,.2f}\n"
        f"💵 ИТОГО остаток наличных: {total_cash:,.2f}\n"
        f"📦 ИТОГО остаток товара: {total_stock:,.2f}\n"
        f"📉 ИТОГО расходы/списания: {total_expenses:,.2f}"
    )
    return "\n".join(lines)


def _build_points_status_block(shops: list[Shop], closed_shifts: list[Shift]) -> str:
    """Список всех точек: закрыта смена или нет."""
    closed_by_shop = {s.shop_id: s for s in closed_shifts}
    lines = ["📍 Точки за день:\n"]
    for shop in shops:
        shift = closed_by_shop.get(shop.id)
        if shift:
            seller_name = shift.seller.full_name if shift.seller else "—"
            lines.append(f"✅ {shop.address} — закрыта ({seller_name})")
        else:
            lines.append(f"❌ {shop.address} — не закрыта")
    return "\n".join(lines)


async def get_daily_report_text(
    session: AsyncSession,
    report_date: date,
    intermediate: bool = False,
) -> str:
    """
    Получить текст отчёта за дату.
    В начале — список всех точек (закрыта/не закрыта), затем детали по закрытым,
    для каждого отчёта — история редактирований (кто, когда, что изменил), затем итоги.
    """
    shops = await shop_repo.get_all_active_shops(session)
    shifts = await shift_repo.get_closed_shifts_by_date(session, report_date)
    points_block = _build_points_status_block(shops, shifts)
    if not shifts:
        body = f"📅 Отчёт за {report_date.strftime('%d.%m.%Y')}\n\nНет данных по закрытым сменам."
    else:
        total_revenue = total_cash = total_stock = total_expenses = 0.0
        lines = [f"📅 Итоговый отчёт за {report_date.strftime('%d.%m.%Y')}\n"]
        for shift in shifts:
            low_revenue = False
            if shift.report and shift.shop_id:
                avg = await shift_repo.get_shop_avg_revenue_before(
                    session, shift.shop_id, report_date, days=AVG_REVENUE_DAYS
                )
                if avg is not None and avg > 0 and shift.report.revenue < avg * LOW_REVENUE_RATIO:
                    low_revenue = True
            lines.append(_format_shift_report(shift, low_revenue_warning=low_revenue))
            if shift.report:
                r = shift.report
                total_revenue += r.revenue
                total_cash += r.cash_balance
                total_stock += r.stock_balance
                total_expenses += r.expenses
                history = await get_edit_history_text(session, r.id)
                if history:
                    lines.append(history)
        lines.append(
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 ИТОГО выручка: {total_revenue:,.2f}\n"
            f"💵 ИТОГО остаток наличных: {total_cash:,.2f}\n"
            f"📦 ИТОГО остаток товара: {total_stock:,.2f}\n"
            f"📉 ИТОГО расходы/списания: {total_expenses:,.2f}"
        )
        body = "\n".join(lines)
    return points_block + "\n\n" + body


async def was_final_report_sent(session: AsyncSession, report_date: date) -> bool:
    """Был ли уже отправлен итоговый отчёт за день."""
    status = await daily_report_status_repo.get_status_by_date(session, report_date)
    return bool(status and status.is_final_sent)


async def mark_final_report_sent(session: AsyncSession, report_date: date) -> None:
    """Отметить, что итоговый отчёт за день отправлен."""
    await daily_report_status_repo.mark_final_sent(session, report_date)


def _week_range(week_end_sunday: date) -> tuple[date, date]:
    """Неделя Пн–Вс: (понедельник, воскресенье). week_end_sunday — дата воскресенья."""
    start = week_end_sunday - timedelta(days=6)
    return start, week_end_sunday


async def get_weekly_analytics_text(
    session: AsyncSession, week_end_sunday: date
) -> str:
    """
    Текст недельной аналитики: общая выручка, топ-3 точки, топ-3 продавца.
    week_end_sunday — воскресенье (конец недели).
    """
    start, end = _week_range(week_end_sunday)
    shifts = await shift_repo.get_closed_shifts_in_date_range(session, start, end)
    shifts_with_revenue = [s for s in shifts if s.report is not None]
    total_revenue = sum(s.report.revenue for s in shifts_with_revenue)

    by_shop: dict[int, float] = defaultdict(float)
    shop_names: dict[int, str] = {}
    by_seller: dict[int, float] = defaultdict(float)
    seller_names: dict[int, str] = {}
    for s in shifts_with_revenue:
        by_shop[s.shop_id] += s.report.revenue
        if s.shop:
            shop_names[s.shop_id] = s.shop.address
        by_seller[s.seller_id] += s.report.revenue
        if s.seller:
            seller_names[s.seller_id] = s.seller.full_name

    top_shops = sorted(by_shop.items(), key=lambda x: -x[1])[:3]
    top_sellers = sorted(by_seller.items(), key=lambda x: -x[1])[:3]

    lines = [
        f"📊 Недельная аналитика (Пн {start.strftime('%d.%m')} – Вс {end.strftime('%d.%m.%Y')})\n",
        f"💰 Общая выручка за неделю: {total_revenue:,.0f} ₽\n",
        "🏆 Топ-3 точки по выручке:",
    ]
    for i, (shop_id, rev) in enumerate(top_shops, 1):
        name = shop_names.get(shop_id, f"Точка {shop_id}")
        lines.append(f"  {i}. {name} — {rev:,.0f} ₽")
    lines.append("\n👤 Топ-3 продавца по выручке:")
    for i, (seller_id, rev) in enumerate(top_sellers, 1):
        name = seller_names.get(seller_id, f"Продавец {seller_id}")
        lines.append(f"  {i}. {name} — {rev:,.0f} ₽")
    return "\n".join(lines)


async def was_weekly_report_sent(session: AsyncSession, week_end_date: date) -> bool:
    """Была ли уже отправлена недельная аналитика за эту неделю (дата воскресенья)."""
    return await weekly_report_status_repo.was_weekly_report_sent(session, week_end_date)


async def mark_weekly_report_sent(session: AsyncSession, week_end_date: date) -> None:
    """Отметить, что недельная аналитика за неделю отправлена."""
    await weekly_report_status_repo.mark_weekly_report_sent(session, week_end_date)
