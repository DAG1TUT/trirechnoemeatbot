"""
FSM для пошагового ввода отчёта при закрытии смены и редактирования после отправки.
"""
from aiogram.fsm.state import State, StatesGroup


class ReportFSM(StatesGroup):
    """Состояния ввода полей отчёта по смене."""

    receipts = State()       # приход
    revenue = State()
    revenue_meat = State()   # для продуктовых: выручка по мясу
    revenue_store = State()  # для продуктовых: выручка по магазину
    terminal_revenue = State()  # терминал (карта)
    cash_revenue = State()   # наличные от выручки
    cash_balance = State()
    stock_balance = State()
    expenses = State()
    surrender_amount = State()  # сдаю
    comment = State()
    confirm = State()
    editing = State()  # ввод нового значения при нажатии «Изменить»
    confirm_big_value = State()  # переспрос при подозрительно большом числе


class EditReportFSM(StatesGroup):
    """Редактирование уже отправленного отчёта (до 24:00 того же дня)."""

    choosing_field = State()
    waiting_value = State()
