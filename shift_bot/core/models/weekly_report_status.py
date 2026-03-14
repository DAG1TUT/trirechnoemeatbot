"""
Статус отправки недельной аналитики (чтобы не слать повторно за одну неделю).
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base, TimestampMixin


class WeeklyReportStatus(Base, TimestampMixin):
    """Неделя задаётся датой воскресенья (конец недели Пн–Вс)."""

    __tablename__ = "weekly_report_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    week_end_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)  # воскресенье
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"WeeklyReportStatus(week_end={self.week_end_date}, sent={self.is_sent})"
