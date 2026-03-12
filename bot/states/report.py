"""
FSM для пошагового ввода отчёта при закрытии смены.
"""
from aiogram.fsm.state import State, StatesGroup


class ReportFSM(StatesGroup):
    """Состояния ввода полей отчёта по смене."""

    revenue = State()
    cash_balance = State()
    stock_balance = State()
    expenses = State()
    comment = State()
    confirm = State()
