"""
Клавиатуры для админа.
"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def kb_admin_main() -> ReplyKeyboardMarkup:
    """Главное меню админа."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🟢 Активные смены")],
            [KeyboardButton(text="👥 Кто где работает")],
            [KeyboardButton(text="📊 Отчет за сегодня")],
            [KeyboardButton(text="📄 Итоговый отчет")],
            [KeyboardButton(text="📅 История")],
            [KeyboardButton(text="📁 Архив отчётов")],
            [KeyboardButton(text="📈 Рейтинг продавцов")],
            [KeyboardButton(text="📈 Рейтинг точек")],
            [KeyboardButton(text="⚠️ Незакрытые точки")],
            [KeyboardButton(text="🚪 Выйти из режима администратора")],
        ],
        resize_keyboard=True,
    )


def kb_seller_rating(seller_rows: list) -> InlineKeyboardMarkup:
    """Кнопки «провалиться в продавца» под рейтингом продавцов."""
    buttons = []
    for r in seller_rows:
        name = (r.seller.full_name or f"ID{r.seller.id}")[:30]
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {name}",
                callback_data=f"seller_rating_{r.seller.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_shop_rating(shop_rows: list) -> InlineKeyboardMarkup:
    """Кнопки «провалиться в точку» под рейтингом точек."""
    buttons = []
    for r in shop_rows:
        addr = (r.shop.address or f"Точка {r.shop.id}")[:30]
        buttons.append([
            InlineKeyboardButton(
                text=f"📍 {addr}",
                callback_data=f"shop_rating_{r.shop.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
