import json
import os
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials


_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_cached_sheet = None


def _get_sheet() -> Optional[gspread.Worksheet]:
    """Лениво инициализирует клиент Google Sheets и возвращает первый лист.

    Ничего не ломает бота: при любой проблеме просто возвращает None.
    """
    global _cached_sheet
    if _cached_sheet is not None:
        return _cached_sheet

    creds_json = os.environ.get("GOOGLE_SHEETS_CREDS_JSON")
    spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
    if not creds_json:
        print("[GSHEETS] disabled: GOOGLE_SHEETS_CREDS_JSON is empty")
        return None
    if not spreadsheet_id:
        print("[GSHEETS] disabled: GOOGLE_SHEETS_SPREADSHEET_ID is empty")
        return None
    try:
        info = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(info, scopes=_SCOPES)
        client = gspread.authorize(credentials)
        sh = client.open_by_key(spreadsheet_id)
        _cached_sheet = sh.sheet1
        print("[GSHEETS] init ok")
        return _cached_sheet
    except Exception as e:
        # Логируем, но не падаем, чтобы бот продолжал работать.
        print(f"[GSHEETS] init error: {e}")
        return None


def append_expense_to_sheet(
    user_id: int,
    amount: float,
    description: str,
    category: str,
    created_at: str,
) -> None:
    """Добавляет строку с тратой в Google Sheets.

    Формат строки: дата/время, user_id, сумма, описание, категория.
    """
    sheet = _get_sheet()
    if sheet is None:
        return
    try:
        sheet.append_row(
            [created_at, str(user_id), float(amount), description, category],
            value_input_option="USER_ENTERED",
        )
    except Exception as e:
        print(f"[GSHEETS] append error: {e}")

