"""
Зависимости для защиты админ-дашборда (сессия + флаг в cookie).
"""
from __future__ import annotations

from urllib.parse import quote

from fastapi import Request
from fastapi.responses import RedirectResponse

ADMIN_SESSION_KEY = "admin_dashboard_ok"


def safe_next_url(raw: str | None, default: str) -> str:
    if not raw or not isinstance(raw, str):
        return default
    s = raw.strip()
    if not s.startswith("/") or s.startswith("//"):
        return default
    return s


async def require_admin_dashboard(request: Request):
    """
    Если не вошли в админку — редирект на /admin/login.
    FastAPI использует возвращённый RedirectResponse как ответ (не вызывает обработчик).
    """
    if request.session.get(ADMIN_SESSION_KEY):
        return True
    next_url = request.url.path
    if request.url.query:
        next_url += "?" + request.url.query
    return RedirectResponse(
        url=f"/admin/login?next={quote(next_url, safe='')}",
        status_code=303,
    )
