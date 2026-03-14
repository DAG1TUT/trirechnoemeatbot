"""FSM для админа: ввод даты для истории отчётов и ввод пароля."""
from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    waiting_report_date = State()
    waiting_archive_period = State()


class AdminLoginFSM(StatesGroup):
    """Ввод пароля администратора."""
    waiting_password = State()