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

# База данных: всегда абсолютный путь к shift_bot/data/shifts.db,
# чтобы не зависеть от папки, из которой запустили бота
_data_dir = _CONFIG_DIR / "data"
_data_dir.mkdir(parents=True, exist_ok=True)
_default_db = _data_dir / "shifts.db"
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{_default_db}",
)
DB_DIR = _data_dir

# Дополнительные админы по telegram_id (через запятую)
ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = (
    {int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()}
    if ADMIN_IDS_STR
    else set()
)
