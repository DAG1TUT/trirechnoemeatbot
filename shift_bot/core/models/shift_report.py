"""
Модель отчёта по смене (гибкая структура для расширения полей).
"""
from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base, TimestampMixin


class ShiftReport(Base, TimestampMixin):
    __tablename__ = "shift_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"), nullable=False, unique=True)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cash_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")

    shift: Mapped["Shift"] = relationship("Shift", back_populates="report")

    def __repr__(self) -> str:
        return f"ShiftReport(shift_id={self.shift_id}, revenue={self.revenue})"
