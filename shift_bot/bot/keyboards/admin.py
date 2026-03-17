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
            [
                KeyboardButton(text="👤 Продавцы"),
                KeyboardButton(text="🏬 Торговые точки"),
            ],
            [KeyboardButton(text="🗑 Удалить данные за дату")],
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


def kb_delete_scope() -> InlineKeyboardMarkup:
    """Выбор: удалить за всю дату / по точке / по продавцу."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Вся дата", callback_data="delete_scope_all")],
        [InlineKeyboardButton(text="📍 По точке", callback_data="delete_scope_shop")],
        [InlineKeyboardButton(text="👤 По продавцу", callback_data="delete_scope_seller")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="delete_cancel")],
    ])


def kb_delete_choose_shop(shops: list) -> InlineKeyboardMarkup:
    """Список точек для удаления данных за дату."""
    buttons = [
        [InlineKeyboardButton(text=shop.address[:35], callback_data=f"delete_shop_{shop.id}")]
        for shop in shops
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="delete_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_delete_choose_seller(sellers: list) -> InlineKeyboardMarkup:
    """Список продавцов для удаления данных за дату."""
    buttons = [
        [InlineKeyboardButton(text=(s.full_name or f"ID{s.id}")[:35], callback_data=f"delete_seller_{s.id}")]
        for s in sellers
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="delete_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_delete_confirm() -> InlineKeyboardMarkup:
    """Подтверждение удаления."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Удалить", callback_data="delete_confirm_yes")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="delete_cancel")],
    ])
