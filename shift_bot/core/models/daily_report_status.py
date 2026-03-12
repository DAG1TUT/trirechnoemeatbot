"""
Статус отправки итогового отчёта за день (чтобы не слать повторно).
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base, TimestampMixin


class DailyReportStatus(Base, TimestampMixin):
    __tablename__ = "daily_report_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    is_final_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)

    def __repr__(self) -> str:
        return f"DailyReportStatus(date={self.report_date}, sent={self.is_final_sent})"
