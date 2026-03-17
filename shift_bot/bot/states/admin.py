"""FSM для админа: ввод даты для истории отчётов и ввод пароля."""
from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    waiting_report_date = State()
    waiting_archive_period = State()
    waiting_delete_date = State()
    # управление продавцами
    managing_sellers = State()
    adding_seller_name = State()
    renaming_seller_choose = State()
    renaming_seller_new_name = State()
    # управление торговыми точками
    managing_shops = State()
    adding_shop_address = State()
    renaming_shop_choose = State()
    renaming_shop_new_address = State()


class AdminLoginFSM(StatesGroup):
    """Ввод пароля администратора."""
    waiting_password = State()