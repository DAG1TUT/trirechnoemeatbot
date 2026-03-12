"""
Модель смены.
"""
from __future__ import annotations

from datetime import date, time
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from core.models.shift_report import ShiftReport


class Shift(Base, TimestampMixin):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"), nullable=False)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.id"), nullable=False)
    shift_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    close_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")  # open | closed

    seller: Mapped["Seller"] = relationship("Seller", back_populates="shifts")
    shop: Mapped["Shop"] = relationship("Shop", back_populates="shifts")
    report: Mapped[Optional["ShiftReport"]] = relationship(
        "ShiftReport", back_populates="shift", uselist=False
    )

    def __repr__(self) -> str:
        return f"Shift(id={self.id}, seller_id={self.seller_id}, shop_id={self.shop_id}, status={self.status})"
