"""
Конфигурация приложения из переменных окружения.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Токен бота: BOT_TOKEN в .env локально, TELEGRAM_BOT_TOKEN на Railway
BOT_TOKEN: str = (
    os.getenv("BOT_TOKEN", "").strip()
    or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
)

# База данных (SQLite по умолчанию, легко заменить на PostgreSQL)
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./data/shifts.db",
)

# Директория для файла БД (для SQLite)
DB_DIR = Path("data")
DB_DIR.mkdir(parents=True, exist_ok=True)

# Дополнительные админы по telegram_id (через запятую)
ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = (
    {int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()}
    if ADMIN_IDS_STR
    else set()
)
