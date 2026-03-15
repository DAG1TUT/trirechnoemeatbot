import json
import os
import sys
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials


def _log(msg: str) -> None:
    print(msg, flush=True)
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_cached_sheet = None
_format_done = False
_log("[GSHEETS] module loaded")


def _setup_format_and_chart(sh: gspread.Spreadsheet) -> None:
    """Один раз: форматирование листа с тратами, лист «Сводка по категориям» и круговая диаграмма."""
    global _format_done
    if _format_done:
        return
    try:
        data_sheet = sh.sheet1
        data_title = data_sheet.title
        data_sheet_id = data_sheet.id

        # Формат первого листа: жирный заголовок, числа с разделителем
        first = data_sheet.row_values(1)
        if not first or all(c == "" for c in first):
            data_sheet.update("A1:E1", [["Дата", "user_id", "Сумма", "Описание", "Категория"]])
        data_sheet.format("A1:E1", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}})
        data_sheet.format("C2:C", {"numberFormat": {"type": "NUMBER", "pattern": "#,##0"}})
        # Заморозить первую строку
        sh.batch_update({
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": data_sheet_id, "gridProperties": {"frozenRowCount": 1}},
                        "fields": "gridProperties.frozenRowCount",
                    }
                }
            ]
        })
        _log("[GSHEETS] data sheet formatted")

        # Лист «Сводка по категориям» (если ещё нет)
        summary_title = "Сводка по категориям"
        try:
            summary_ws = sh.worksheet(summary_title)
        except gspread.WorksheetNotFound:
            summary_ws = sh.add_worksheet(title=summary_title, rows=50, cols=6)
            # Формула: сумма по категориям из первого листа (E = категория, C = сумма)
            formula = f'=QUERY(\'{data_title}\'!A:E,"select E, sum(C) where A is not null group by E label sum(C) \'Сумма\'",1)'
            summary_ws.update_acell("A1", formula)
            summary_ws.format("A1:B1", {"textFormat": {"bold": True}})
            _log("[GSHEETS] summary sheet created")

            # Круговая диаграмма по данным сводки (категория = A, сумма = B)
            summary_id = summary_ws.id
            sh.batch_update({
                "requests": [
                    {
                        "addChart": {
                            "chart": {
                                "spec": {
                                    "title": "Траты по категориям",
                                    "pieChart": {
                                        "legendPosition": "RIGHT_LEGEND",
                                        "domain": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": summary_id,
                                                        "startRowIndex": 1,
                                                        "endRowIndex": 50,
                                                        "startColumnIndex": 0,
                                                        "endColumnIndex": 1,
                                                    }
                                                ]
                                            }
                                        },
                                        "series": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": summary_id,
                                                        "startRowIndex": 1,
                                                        "endRowIndex": 50,
                                                        "startColumnIndex": 1,
                                                        "endColumnIndex": 2,
                                                    }
                                                ]
                                            }
                                        },
                                    },
                                    "position": {
                                        "overlayPosition": {
                                            "anchorCell": {"sheetId": summary_id, "rowIndex": 0, "columnIndex": 3},
                                            "offsetXPixels": 20,
                                            "offsetYPixels": 20,
                                            "widthPixels": 420,
                                            "heightPixels": 320,
                                        }
                                    },
                                }
                            }
                        }
                    }
                ]
            })
            _log("[GSHEETS] pie chart added")
        _format_done = True
    except Exception as e:
        _log(f"[GSHEETS] setup_format_and_chart error: {e}")


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
        _log("[GSHEETS] disabled: GOOGLE_SHEETS_CREDS_JSON is empty")
        return None
    if not spreadsheet_id:
        _log("[GSHEETS] disabled: GOOGLE_SHEETS_SPREADSHEET_ID is empty")
        return None
    try:
        info = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(info, scopes=_SCOPES)
        client = gspread.authorize(credentials)
        sh = client.open_by_key(spreadsheet_id)
        _cached_sheet = sh.sheet1
        # Заголовки в первой строке, если лист пустой (дублируем для совместимости)
        try:
            first = _cached_sheet.row_values(1)
            if not first or all(c == "" for c in first):
                _cached_sheet.update("A1:E1", [["created_at", "user_id", "amount", "description", "category"]])
                _log("[GSHEETS] headers written")
        except Exception:
            pass
        _setup_format_and_chart(sh)
        _log("[GSHEETS] init ok")
        return _cached_sheet
    except Exception as e:
        _log(f"[GSHEETS] init error: {e}")
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
    _log("[GSHEETS] append_expense_to_sheet called")
    sheet = _get_sheet()
    if sheet is None:
        _log("[GSHEETS] skip: sheet not available (check Variables or init logs above)")
        return
    try:
        sheet.append_row(
            [created_at, str(user_id), float(amount), description, category],
            value_input_option="USER_ENTERED",
        )
        _log("[GSHEETS] row appended ok")
    except Exception as e:
        _log(f"[GSHEETS] append error: {e}")

