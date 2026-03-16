"""
Конфигурация приложения из переменных окружения.
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv

# Папка, где лежит этот config.py (чтобы находить файлы настроек при любом запуске)
_CONFIG_DIR = Path(__file__).resolve().parent

# Загрузка настроек. Файл с токеном загружаем последним с override=True,
# иначе старый BOT_TOKEN из .env не перезапишется.
load_dotenv(_CONFIG_DIR / ".env")
load_dotenv(_CONFIG_DIR / "config.env")
load_dotenv(_CONFIG_DIR / "ВСТАВЬ_ТОКЕН_СЮДА.txt", override=True)

# Токен бота: убираем пробелы и невидимые символы (часто попадают при копировании)
_raw = os.getenv("BOT_TOKEN", "")
BOT_TOKEN = re.sub(r"[\s\u200b\u200c\u200d\ufeff]+", "", _raw).strip() if _raw else ""

# База данных: по умолчанию SQLite (shift_bot/data/shifts.db).
# Для Railway/продакшена задайте DATABASE_URL от PostgreSQL — данные не пропадут после деплоя.
_data_dir = _CONFIG_DIR / "data"
_data_dir.mkdir(parents=True, exist_ok=True)
_default_db = _data_dir / "shifts.db"
_raw_url = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{_default_db}")
# Railway даёт URL вида postgres:// или postgresql:// — подставляем драйвер asyncpg для async
if "postgresql+asyncpg" not in _raw_url and (
    _raw_url.startswith("postgresql://") or _raw_url.startswith("postgres://")
):
    _raw_url = "postgresql+asyncpg://" + _raw_url.split("://", 1)[1]
DATABASE_URL: str = _raw_url
DB_DIR = _data_dir

# Дополнительные админы по telegram_id (через запятую)
ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = (
    {int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()}
    if ADMIN_IDS_STR
    else set()
)

# Один пароль для входа по кнопке «Администратор». Берётся из .env или этот по умолчанию.
ADMIN_PASSWORD: str = (os.getenv("ADMIN_PASSWORD") or "admin").strip()
