# -*- coding: utf-8 -*-
"""Хранение расходов в SQLite."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "expenses.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_expense(user_id: int, amount: float, description: str, category: str, created_at: str | None = None):
    conn = get_connection()
    if created_at is None:
        created_at = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO expenses (user_id, amount, description, category, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, amount, description, category, created_at),
    )
    conn.commit()
    conn.close()
    return created_at


def get_expenses(user_id: int, limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, amount, description, category, created_at FROM expenses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_expense_by_id(user_id: int, expense_id: int):
    """Одна трата по id (только своего пользователя)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, amount, description, category, created_at FROM expenses WHERE user_id = ? AND id = ?",
        (user_id, expense_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_expense(user_id: int, expense_id: int) -> bool:
    """Удаляет трату. Возвращает True, если запись была и удалена."""
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM expenses WHERE user_id = ? AND id = ?",
        (user_id, expense_id),
    )
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def update_expense_category(user_id: int, expense_id: int, category: str) -> bool:
    """Меняет категорию траты. Возвращает True, если запись обновлена."""
    conn = get_connection()
    cur = conn.execute(
        "UPDATE expenses SET category = ? WHERE user_id = ? AND id = ?",
        (category, user_id, expense_id),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def delete_all_expenses(user_id: int) -> int:
    """Удаляет все траты пользователя. Возвращает количество удалённых записей."""
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM expenses WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    deleted = cur.rowcount or 0
    conn.close()
    return deleted


def get_summary_by_category(user_id: int, period_days: int = 30):
    conn = get_connection()
    since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    since = (since - timedelta(days=period_days)).isoformat()
    rows = conn.execute(
        """SELECT category, SUM(amount) as total FROM expenses 
           WHERE user_id = ? AND created_at >= ? GROUP BY category ORDER BY total DESC""",
        (user_id, since),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total(user_id: int, period_days: int = 30):
    conn = get_connection()
    since = (datetime.now() - timedelta(days=period_days)).isoformat()
    row = conn.execute(
        "SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND created_at >= ?",
        (user_id, since),
    ).fetchone()
    conn.close()
    return row["total"] or 0


def get_expenses_by_category(user_id: int, category: str, period_days: int = 30, limit: int = 50):
    """Траты по одной категории (category — подстрока названия, например «еда»)."""
    conn = get_connection()
    since = (datetime.now() - timedelta(days=period_days)).isoformat()
    rows = conn.execute(
        """SELECT amount, description, created_at FROM expenses 
           WHERE user_id = ? AND created_at >= ? AND category LIKE ? 
           ORDER BY created_at DESC LIMIT ?""",
        (user_id, since, f"%{category}%", limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_totals(user_id: int, period_days: int = 30):
    """Названия категорий и суммы за период (для подсказки в /cat)."""
    return get_summary_by_category(user_id, period_days)
