from aiogram import Router

from bot.handlers import common, seller, admin, report_fsm

def setup_routers() -> Router:
    root = Router()
    root.include_router(common.router)
    root.include_router(seller.router)
    root.include_router(report_fsm.router)
    root.include_router(admin.router)
    return root
