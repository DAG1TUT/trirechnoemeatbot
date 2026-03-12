"""
Базовый репозиторий с общими зависимостями от сессии.
"""
from sqlalchemy.ext.asyncio import AsyncSession

# Тип для внедрения сессии в handlers
# В реальных методах репозиториев принимаем session: AsyncSession
