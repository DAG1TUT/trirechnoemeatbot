"""
Клавиатуры для продавца.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from core.models.seller import Seller
from core.models.shop import Shop


def kb_seller_main() -> ReplyKeyboardMarkup:
    """Главное меню продавца: Открыть смену, Моя смена, Закрыть смену, Редактировать отчёт, Выйти."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Открыть смену")],
            [KeyboardButton(text="📋 Моя смена")],
            [KeyboardButton(text="✅ Закрыть смену")],
            [KeyboardButton(text="✏️ Редактировать отчёт")],
            [KeyboardButton(text="🚪 Выйти / Сменить привязку")],
        ],
        resize_keyboard=True,
    )


def kb_choose_seller(sellers: list[Seller], add_admin_button: bool = True) -> InlineKeyboardMarkup:
    """Выбор продавца для привязки + кнопка «Администратор» (по паролю)."""
    rows = []
    for s in sellers:
        if s.telegram_id is None:
            rows.append([InlineKeyboardButton(text=s.full_name, callback_data=f"bind_seller_{s.id}")])
    if add_admin_button:
        rows.append([InlineKeyboardButton(text="👑 Администратор", callback_data="admin_login_start")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_choose_shop(shops: list[Shop]) -> InlineKeyboardMarkup:
    """Выбор торговой точки при открытии смены."""
    rows = [
        [InlineKeyboardButton(text=shop.address, callback_data=f"open_shop_{shop.id}")]
        for shop in shops
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_confirm_close_shift() -> InlineKeyboardMarkup:
    """Подтверждение закрытия смены после ввода всех полей отчёта."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="report_confirm")],
        [
            InlineKeyboardButton(text="✏️ Изменить", callback_data="report_edit"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="report_cancel"),
        ],
    ])


def kb_edit_report_field(is_grocery: bool = False) -> InlineKeyboardMarkup:
    """Выбор поля отчёта для изменения. is_grocery — показывать выручка по мясу/магазину."""
    rows = []
    rows.append([InlineKeyboardButton(text="📥 Приход", callback_data="report_edit_receipts")])
    if is_grocery:
        rows.append([InlineKeyboardButton(text="🥩 Выручка по мясу", callback_data="report_edit_revenue_meat")])
        rows.append([InlineKeyboardButton(text="🏪 Выручка по магазину", callback_data="report_edit_revenue_store")])
        rows.append([InlineKeyboardButton(text="💰 Выручка итого", callback_data="report_edit_revenue")])
    else:
        rows.append([InlineKeyboardButton(text="💰 Выручка", callback_data="report_edit_revenue")])
    rows.extend([
        [InlineKeyboardButton(text="💳 Терминал", callback_data="report_edit_terminal_revenue")],
        [InlineKeyboardButton(text="💵 Наличные от выручки", callback_data="report_edit_cash_revenue")],
        [InlineKeyboardButton(text="💵 Остаток наличных", callback_data="report_edit_cash")],
        [InlineKeyboardButton(text="📦 Остаток товара", callback_data="report_edit_stock")],
        [InlineKeyboardButton(text="📉 Расходы", callback_data="report_edit_expenses")],
        [InlineKeyboardButton(text="📤 Сдаю", callback_data="report_edit_surrender_amount")],
        [InlineKeyboardButton(text="💬 Комментарий", callback_data="report_edit_comment")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="report_edit_back")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_after_shift_opened(shift_id: int) -> InlineKeyboardMarkup:
    """Кнопки под сообщением «Смена открыта» — shift_id в callback, чтобы точно находить смену."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Моя смена", callback_data=f"my_shift_{shift_id}"),
            InlineKeyboardButton(text="✅ Закрыть смену", callback_data=f"close_shift_{shift_id}"),
        ],
    ])


def kb_edit_report_after_submit(is_grocery: bool = False) -> InlineKeyboardMarkup:
    """Выбор поля при редактировании уже отправленного отчёта + Готово. is_grocery — показывать выручка по мясу/магазину."""
    rows = []
    rows.append([InlineKeyboardButton(text="📥 Приход", callback_data="edit_report_field_receipts")])
    if is_grocery:
        rows.append([InlineKeyboardButton(text="🥩 Выручка по мясу", callback_data="edit_report_field_revenue_meat")])
        rows.append([InlineKeyboardButton(text="🏪 Выручка по магазину", callback_data="edit_report_field_revenue_store")])
        rows.append([InlineKeyboardButton(text="💰 Выручка итого", callback_data="edit_report_field_revenue")])
    else:
        rows.append([InlineKeyboardButton(text="💰 Выручка", callback_data="edit_report_field_revenue")])
    rows.extend([
        [InlineKeyboardButton(text="💳 Терминал", callback_data="edit_report_field_terminal_revenue")],
        [InlineKeyboardButton(text="💵 Наличные от выручки", callback_data="edit_report_field_cash_revenue")],
        [InlineKeyboardButton(text="💵 Остаток наличных", callback_data="edit_report_field_cash")],
        [InlineKeyboardButton(text="📦 Остаток товара", callback_data="edit_report_field_stock")],
        [InlineKeyboardButton(text="📉 Расходы", callback_data="edit_report_field_expenses")],
        [InlineKeyboardButton(text="📤 Сдаю", callback_data="edit_report_field_surrender_amount")],
        [InlineKeyboardButton(text="💬 Комментарий", callback_data="edit_report_field_comment")],
        [InlineKeyboardButton(text="✅ Готово", callback_data="edit_report_done")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_edit_report_offer(shift_id: int) -> InlineKeyboardMarkup:
    """Кнопка «Редактировать отчёт» после закрытия смены (до 24:00)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать отчёт", callback_data=f"edit_report_offer_{shift_id}")]
    ])
