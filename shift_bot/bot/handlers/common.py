"""
Общие обработчики: /start, привязка продавца, вход администратора по паролю, ошибки.
"""
import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb_seller_main, kb_admin_main, kb_choose_seller
from bot.keyboards.common import kb_cancel
from bot.store import LOGGED_OUT_ADMIN_IDS, OPEN_SHIFT_BY_TELEGRAM
from bot.states.admin import AdminLoginFSM
from bot.middlewares.auth import get_session, get_seller, get_role
from config import ADMIN_PASSWORD
from repositories import admin_repo
from services import seller_service

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, session=None, role: str = "", seller=None, **kwargs):
    """Приветствие и главное меню в зависимости от роли."""
    session = session or kwargs.get("session")
    role = role or kwargs.get("role", "guest")
    seller = seller or kwargs.get("seller")

    if role == "admin":
        await message.answer(
            "👋 Добро пожаловать! Вы вошли как руководитель.\n\n"
            "Используйте меню ниже для просмотра смен и отчётов.",
            reply_markup=kb_admin_main(),
        )
        return
    if role == "seller":
        await message.answer(
            f"👋 Здравствуйте, {seller.full_name}!\n\n"
            "Выберите действие в меню ниже.",
            reply_markup=kb_seller_main(),
        )
        return
    # Гость: предложить привязаться к продавцу
    sellers = await seller_service.get_sellers_for_binding(session)
    if not sellers or all(s.telegram_id is not None for s in sellers):
        await message.answer(
            "Список продавцов для привязки пуст или все аккаунты уже привязаны. "
            "Обратитесь к руководителю."
        )
        return
    # Показываем только непривязанных
    to_show = [s for s in sellers if s.telegram_id is None]
    if not to_show:
        await message.answer("Все продавцы уже привязаны. Обратитесь к руководителю.")
        return
    await message.answer(
        "👋 Добро пожаловать! Выберите себя из списка продавцов или войдите как руководитель:",
        reply_markup=kb_choose_seller(to_show),
    )


@router.callback_query(F.data == "admin_login_start")
async def cb_admin_login_start(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Гость нажал «Администратор» — запрашиваем пароль."""
    if not ADMIN_PASSWORD:
        await callback.answer(
            "Вход по паролю не настроен. Обратитесь к разработчику.",
            show_alert=True,
        )
        return
    await state.set_state(AdminLoginFSM.waiting_password)
    await callback.answer()
    await callback.message.edit_text(
        "👑 Вход как руководитель.\nВведите пароль администратора:",
        reply_markup=kb_cancel(),
    )


@router.message(AdminLoginFSM.waiting_password, F.text)
async def admin_password_entered(message: Message, state: FSMContext, session, **kwargs):
    """Проверка пароля администратора."""
    password = (message.text or "").strip()
    if password != ADMIN_PASSWORD:
        await state.clear()
        await message.answer("❌ Неверный пароль.")
        return
    telegram_id = message.from_user.id
    full_name = (message.from_user.full_name or "").strip() or "Руководитель"
    await admin_repo.ensure_admin(session, telegram_id, full_name)
    LOGGED_OUT_ADMIN_IDS.discard(telegram_id)
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать! Вы вошли как руководитель.\n\n"
        "Используйте меню ниже для просмотра смен и отчётов.",
        reply_markup=kb_admin_main(),
    )


@router.callback_query(AdminLoginFSM.waiting_password, F.data == "report_cancel")
async def admin_login_cancel(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отмена ввода пароля администратора."""
    await state.clear()
    await callback.answer("Отменено")
    await callback.message.edit_text("Вход отменён. Нажмите /start для выбора роли.")


@router.message(F.text == "🚪 Выйти / Сменить привязку")
async def seller_logout(message: Message, session, role, **kwargs):
    """Продавец выходит из аккаунта и возвращается к выбору фамилии."""
    if role != "seller":
        return
    telegram_id = message.from_user.id
    ok = await seller_service.unbind_seller(session, telegram_id)
    OPEN_SHIFT_BY_TELEGRAM.pop(telegram_id, None)
    if not ok:
        await message.answer("Не удалось выйти. Попробуйте /start.")
        return
    sellers = await seller_service.get_sellers_for_binding(session)
    to_show = [s for s in sellers if s.telegram_id is None]
    if not to_show:
        await message.answer("Список продавцов для привязки пуст. Обратитесь к руководителю.")
        return
    await message.answer(
        "Вы вышли из аккаунта. Выберите себя из списка или войдите как руководитель:",
        reply_markup=kb_choose_seller(to_show),
    )


@router.callback_query(F.data.startswith("bind_seller_"))
async def cb_bind_seller(callback: CallbackQuery, session=None, **kwargs):
    """Привязка telegram_id к выбранному продавцу."""
    session = session or kwargs.get("session")
    seller_id = int(callback.data.split("_")[-1])
    telegram_id = callback.from_user.id
    seller = await seller_service.bind_seller(session, seller_id, telegram_id)
    await callback.answer()
    if seller:
        await callback.message.edit_text(
            f"✅ Вы привязаны как {seller.full_name}. Нажмите /start для обновления меню."
        )
        await callback.message.answer(
            f"👋 Здравствуйте, {seller.full_name}! Выберите действие:",
            reply_markup=kb_seller_main(),
        )
    else:
        await callback.message.edit_text("❌ Не удалось привязать аккаунт. Попробуйте снова или обратитесь к руководителю.")
