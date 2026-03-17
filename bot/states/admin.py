"""FSM для админа: ввод даты для истории отчётов."""
from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    waiting_report_date = State()
    managing_sellers = State()
    managing_shops = State()