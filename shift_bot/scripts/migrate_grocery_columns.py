"""
Одноразовая миграция: добавить колонки в shift_reports (revenue_meat, revenue_store,
receipts, terminal_revenue, cash_revenue, surrender_amount).
Запуск: python -m scripts.migrate_grocery_columns
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from core.database import engine

NEW_COLUMNS = [
    ("revenue_meat", "REAL"),
    ("revenue_store", "REAL"),
    ("receipts", "REAL"),
    ("terminal_revenue", "REAL"),
    ("cash_revenue", "REAL"),
    ("surrender_amount", "REAL"),
]


async def run():
    async with engine.begin() as conn:
        r = await conn.execute(text("PRAGMA table_info(shift_reports)"))
        rows = r.fetchall()
        names = [row[1] for row in rows]
        for col_name, col_type in NEW_COLUMNS:
            if col_name not in names:
                await conn.execute(text(f"ALTER TABLE shift_reports ADD COLUMN {col_name} {col_type}"))
                print(f"Добавлена колонка {col_name}.")
    print("Миграция завершена.")


if __name__ == "__main__":
    asyncio.run(run())
