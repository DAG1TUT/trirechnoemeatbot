"""
Общие клавиатуры.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def kb_cancel() -> InlineKeyboardMarkup:
    """Кнопка отмены (для FSM)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="report_cancel")]
    ])
