"""
Модель отчёта по смене (гибкая структура для расширения полей).
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from core.models.shift_report_edit import ShiftReportEdit


class ShiftReport(Base, TimestampMixin):
    __tablename__ = "shift_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"), nullable=False, unique=True)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Для продуктовых магазинов (Казаки, Строитель): выручка по мясу и по магазину отдельно
    revenue_meat: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    revenue_store: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    # Выручка: по терминалу (карта) и наличными
    terminal_revenue: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    cash_revenue: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    receipts: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # приход
    surrender_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # сдаю
    cash_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")

    shift: Mapped["Shift"] = relationship("Shift", back_populates="report")
    edits: Mapped[List["ShiftReportEdit"]] = relationship(
        "ShiftReportEdit",
        back_populates="shift_report",
    )

    def __repr__(self) -> str:
        return f"ShiftReport(shift_id={self.shift_id}, revenue={self.revenue})"
