"""
Общие клавиатуры.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def kb_cancel() -> InlineKeyboardMarkup:
    """Кнопка отмены (для FSM)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="report_cancel")]
    ])


def kb_cancel_back() -> InlineKeyboardMarkup:
    """Отмена и Назад (при вводе полей отчёта, не на первом шаге)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="report_step_back"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="report_cancel"),
        ]
    ])
