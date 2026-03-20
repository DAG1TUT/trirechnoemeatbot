"""
Модель продавца.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base, TimestampMixin


class Seller(Base, TimestampMixin):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    web_password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # relationships
    shifts: Mapped[list["Shift"]] = relationship("Shift", back_populates="seller")

    def __repr__(self) -> str:
        return f"Seller(id={self.id}, full_name={self.full_name!r}, telegram_id={self.telegram_id})"
