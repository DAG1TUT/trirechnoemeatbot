"""
Хранилище открытых смен по telegram_id (в памяти бота).
После открытия смены сюда пишем данные и по ним показываем «Моя смена» / «Закрыть смену» без запроса к БД.
"""
# telegram_id -> {"shift_id": int, "seller_id": int, "address": str, "date_str": str, "open_time_str": str}
OPEN_SHIFT_BY_TELEGRAM: dict[int, dict] = {}

# telegram_id, нажавшие «Выйти из режима администратора» (до перезапуска бота не считаются админами)
LOGGED_OUT_ADMIN_IDS: set[int] = set()
