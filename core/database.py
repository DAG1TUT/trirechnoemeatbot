"""
Подключение к БД: async engine и фабрика сессий.
Готово к замене на PostgreSQL сменой DATABASE_URL.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import DATABASE_URL as _RAW_DATABASE_URL
from core.models.base import Base
from core import models  # noqa: F401 — регистрация всех моделей в Base.metadata


def _make_async_url(url: str) -> str:
    """Гарантировать, что используется async‑драйвер (asyncpg) для PostgreSQL."""
    if "postgresql+asyncpg" in url:
        return url
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    return url


DATABASE_URL = _make_async_url(_RAW_DATABASE_URL)

# echo=True для отладки SQL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield async session for dependency injection."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Создание таблиц при старте приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
