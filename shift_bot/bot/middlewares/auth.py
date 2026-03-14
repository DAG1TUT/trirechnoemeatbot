"""
Middleware: определение роли (админ/продавец/гость) и внедрение сессии БД.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_IDS
from core.database import async_session_factory
from repositories import admin_repo, seller_repo
from bot.store import LOGGED_OUT_ADMIN_IDS


def get_session(event: TelegramObject) -> AsyncSession | None:
    """Достать сессию из данных события (после middleware)."""
    return event.data.get("session")


def get_seller(event: TelegramObject):
    """Достать объект продавца (или None)."""
    return event.data.get("seller")


def get_role(event: TelegramObject) -> str:
    """Роль: admin | seller | guest."""
    return event.data.get("role", "guest")


class AuthMiddleware(BaseMiddleware):
    """Определяет роль пользователя и открывает сессию БД."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = getattr(event, "from_user", None)
        if not user and getattr(event, "message", None):
            user = getattr(event.message, "from_user", None)
        telegram_id = user.id if user else None

        async with async_session_factory() as session:
            data["session"] = session
            role = "guest"
            seller = None

            if telegram_id is not None:
                # Проверка админа: сначала из .env, потом из БД (если не вышел из режима админа)
                if telegram_id in LOGGED_OUT_ADMIN_IDS:
                    pass  # не даём роль админа
                elif telegram_id in ADMIN_IDS:
                    role = "admin"
                else:
                    admin = await admin_repo.get_admin_by_telegram_id(session, telegram_id)
                    if admin:
                        role = "admin"
                if role != "admin":
                    seller = await seller_repo.get_seller_by_telegram_id(session, telegram_id)
                    if seller:
                        role = "seller"

            data["role"] = role
            data["seller"] = seller
            data["telegram_id"] = telegram_id

            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
