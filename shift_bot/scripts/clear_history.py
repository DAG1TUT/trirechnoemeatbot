"""
Очистка истории по точкам: удаляет все смены, отчёты и служебные статусы.
Продавцы, точки и админы остаются.
Запуск: из папки shift_bot — python -m scripts.clear_history
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import delete
from core.database import async_session_factory
from core.models.shift_report_edit import ShiftReportEdit
from core.models.shift_report import ShiftReport
from core.models.shift import Shift
from core.models.daily_report_status import DailyReportStatus
from core.models.weekly_report_status import WeeklyReportStatus


async def run():
    async with async_session_factory() as session:
        # Порядок важен из‑за внешних ключей
        r1 = await session.execute(delete(ShiftReportEdit))
        r2 = await session.execute(delete(ShiftReport))
        r3 = await session.execute(delete(Shift))
        r4 = await session.execute(delete(DailyReportStatus))
        r5 = await session.execute(delete(WeeklyReportStatus))
        await session.commit()
        print("Очищено:")
        print("  — история изменений отчётов (shift_report_edits)")
        print("  — отчёты по сменам (shift_reports)")
        print("  — смены (shifts)")
        print("  — статусы дневных отчётов (daily_report_status)")
        print("  — статусы недельных отчётов (weekly_report_status)")
        print("Продавцы, точки и админы не тронуты.")


if __name__ == "__main__":
    asyncio.run(run())
