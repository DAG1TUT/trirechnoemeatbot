"""
Seed-данные: тестовые продавцы, торговые точки, один админ.
Запуск: python -m scripts.seed
"""
import asyncio
import os
import sys

# Корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select
from core.database import init_db, async_session_factory
from core.models.seller import Seller
from core.models.shop import Shop
from core.models.admin import Admin


SELLERS = [
    "Продавец 1",
    "Продавец 2",
    "Продавец 3",
    "Продавец 4",
]

SHOPS = [
    "ул. Ленина, д. 10",
    "ул. Мира, д. 5",
    "пр. Победы, д. 20",
    "ул. Гагарина, д. 15",
]


async def seed() -> None:
    await init_db()
    async with async_session_factory() as session:
        # Продавцы
        r = await session.execute(select(Seller))
        if r.scalars().first() is not None:
            print("Продавцы уже есть, пропуск.")
        else:
            for name in SELLERS:
                session.add(Seller(full_name=name, telegram_id=None, is_active=True))
            await session.flush()
            print(f"Добавлено продавцов: {len(SELLERS)}")

        # Торговые точки
        r = await session.execute(select(Shop))
        if r.scalars().first() is not None:
            print("Торговые точки уже есть, пропуск.")
        else:
            for address in SHOPS:
                session.add(Shop(address=address, is_active=True))
            await session.flush()
            print(f"Добавлено точек: {len(SHOPS)}")

        # Один админ (telegram_id нужно заменить на реальный или задать в .env ADMIN_IDS)
        r = await session.execute(select(Admin))
        if r.scalars().first() is not None:
            print("Админы уже есть, пропуск.")
        else:
            # По умолчанию заглушка; реальный telegram_id задайте в .env как ADMIN_IDS или добавьте вручную в БД
            session.add(Admin(telegram_id=0, full_name="Руководитель"))
            await session.flush()
            print("Добавлен админ (telegram_id=0). Задайте ADMIN_IDS в .env или обновите запись в БД.")

        await session.commit()
    print("Seed завершён.")


if __name__ == "__main__":
    asyncio.run(seed())
