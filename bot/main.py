"""
Инициализация бота: диспетчер, роутеры, middleware.
"""
import logging

from aiogram import Dispatcher

from bot.handlers import setup_routers
from bot.middlewares.auth import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

dp = Dispatcher()
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())
router = setup_routers()
dp.include_router(router)
