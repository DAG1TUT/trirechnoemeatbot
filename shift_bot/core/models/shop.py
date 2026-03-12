"""
Модель торговой точки.
"""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base, TimestampMixin


class Shop(Base, TimestampMixin):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    shifts: Mapped[list["Shift"]] = relationship("Shift", back_populates="shop")

    def __repr__(self) -> str:
        return f"Shop(id={self.id}, address={self.address!r})"
