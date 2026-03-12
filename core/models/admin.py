"""
Модель администратора (руководителя).
"""
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base, TimestampMixin


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"Admin(id={self.id}, telegram_id={self.telegram_id}, full_name={self.full_name!r})"
