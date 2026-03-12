"""
Клавиатуры для продавца.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from core.models.seller import Seller
from core.models.shop import Shop


def kb_seller_main() -> ReplyKeyboardMarkup:
    """Главное меню продавца: Открыть смену, Моя смена, Закрыть смену."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Открыть смену")],
            [KeyboardButton(text="📋 Моя смена")],
            [KeyboardButton(text="✅ Закрыть смену")],
        ],
        resize_keyboard=True,
    )


def kb_choose_seller(sellers: list[Seller]) -> InlineKeyboardMarkup:
    """Выбор продавца для привязки telegram_id."""
    rows = []
    for s in sellers:
        # Не показываем уже привязанных (опционально: можно показывать всех)
        if s.telegram_id is None:
            rows.append([InlineKeyboardButton(text=s.full_name, callback_data=f"bind_seller_{s.id}")])
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
        [InlineKeyboardButton(text="❌ Отмена", callback_data="report_cancel")],
    ])


def kb_after_shift_opened(shift_id: int) -> InlineKeyboardMarkup:
    """Кнопки под сообщением «Смена открыта» — shift_id в callback, чтобы точно находить смену."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Моя смена", callback_data=f"my_shift_{shift_id}"),
            InlineKeyboardButton(text="✅ Закрыть смену", callback_data=f"close_shift_{shift_id}"),
        ],
    ])
