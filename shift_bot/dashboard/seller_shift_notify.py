"""
Уведомления админам в Telegram после закрытия смены из веб-кабинета
(логика как в bot/handlers/report_fsm.py после report_confirm).
"""
from __future__ import annotations

import logging
from datetime import date

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_IDS, BOT_TOKEN
from repositories import admin_repo, shift_repo, shop_repo
from services import report_service

logger = logging.getLogger(__name__)


async def maybe_send_daily_final_and_weekly_reports(session: AsyncSession) -> None:
    """Если за сегодня закрыты все точки — один раз отправить итоговый дневной отчёт; по воскресеньям — недельную аналитику."""
    if not BOT_TOKEN:
        logger.debug("BOT_TOKEN not set, skip Telegram notifications after web shift close.")
        return

    today = date.today()
    closed = await shift_repo.get_closed_shifts_by_date(session, today)
    all_shops = await shop_repo.get_all_active_shops(session)
    closed_shop_ids = {s.shop_id for s in closed}
    all_shop_ids = {s.id for s in all_shops}
    if not all_shop_ids or closed_shop_ids < all_shop_ids:
        return

    already_sent = await report_service.was_final_report_sent(session, today)
    if already_sent:
        return

    report_text = await report_service.get_daily_report_text(session, today)
    admin_ids = list(await admin_repo.get_all_admin_telegram_ids(session))
    for aid in ADMIN_IDS:
        if aid not in admin_ids:
            admin_ids.append(aid)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    try:
        for aid in admin_ids:
            try:
                await bot.send_message(
                    aid,
                    "📬 Итоговый отчёт за день (все точки закрыты):\n\n" + report_text,
                )
            except Exception as e:
                logger.exception("Send final report to admin %s: %s", aid, e)
        await report_service.mark_final_report_sent(session, today)

        if today.weekday() == 6:
            if not await report_service.was_weekly_report_sent(session, today):
                weekly_text = await report_service.get_weekly_analytics_text(session, today)
                for aid in admin_ids:
                    try:
                        await bot.send_message(
                            aid,
                            "📬 Недельная аналитика (все точки закрыты в воскресенье):\n\n"
                            + weekly_text,
                        )
                    except Exception as e:
                        logger.exception("Send weekly report to admin %s: %s", aid, e)
                await report_service.mark_weekly_report_sent(session, today)
    finally:
        await bot.session.close()
