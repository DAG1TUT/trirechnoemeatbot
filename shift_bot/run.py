"""
Точка входа: инициализация БД, запуск бота.
"""
import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from core.database import init_db
from bot.main import dp

logger = logging.getLogger(__name__)


async def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set. Create .env from .env.example and set BOT_TOKEN.")
        return
    await init_db()
    logger.info("Database initialized.")
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
