"""
Сервис отчётов: сборка текста итогового/промежуточного отчёта за день.
Архитектура готова к добавлению экспорта в Excel (отдельный модуль).
"""
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.shift import Shift
from repositories import daily_report_status_repo, shift_repo


def _format_shift_report(shift: Shift) -> str:
    """Форматирование одной смены для отчёта."""
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
    return (
        f"📍 {address}\n"
        f"👤 {seller_name}\n"
        f"💰 Выручка: {revenue:,.2f}\n"
        f"💵 Остаток наличных: {cash:,.2f}\n"
        f"📦 Остаток товара: {stock:,.2f}\n"
        f"📉 Расходы/списания: {expenses:,.2f}\n"
        f"💬 Комментарий: {comment}\n"
    )


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


async def get_daily_report_text(
    session: AsyncSession,
    report_date: date,
    intermediate: bool = False,
) -> str:
    """
    Получить текст отчёта за дату.
    intermediate=True — промежуточный (все закрытые на момент запроса);
    intermediate=False — то же самое, но используется для итогового сообщения.
    """
    shifts = await shift_repo.get_closed_shifts_by_date(session, report_date)
    return build_daily_report_text(shifts, report_date)


async def was_final_report_sent(session: AsyncSession, report_date: date) -> bool:
    """Был ли уже отправлен итоговый отчёт за день."""
    status = await daily_report_status_repo.get_status_by_date(session, report_date)
    return bool(status and status.is_final_sent)


async def mark_final_report_sent(session: AsyncSession, report_date: date) -> None:
    """Отметить, что итоговый отчёт за день отправлен."""
    await daily_report_status_repo.mark_final_sent(session, report_date)
