"""
Клавиатуры для админа.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def kb_admin_main() -> ReplyKeyboardMarkup:
    """Главное меню админа."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🟢 Активные смены")],
            [KeyboardButton(text="👥 Кто где работает")],
            [KeyboardButton(text="📊 Отчет за сегодня")],
            [KeyboardButton(text="📄 Итоговый отчет")],
            [KeyboardButton(text="📅 История")],
            [KeyboardButton(text="⚠️ Незакрытые точки")],
        ],
        resize_keyboard=True,
    )
