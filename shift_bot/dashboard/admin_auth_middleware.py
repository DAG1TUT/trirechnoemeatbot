"""
Защита админ-дашборда паролем (сессия в том же cookie, что и seller-cabinet).
"""
from __future__ import annotations

from urllib.parse import quote

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

ADMIN_SESSION_KEY = "admin_dashboard_ok"


def _is_public_path(path: str) -> bool:
    """Пути без проверки пароля админки."""
    if path in ("/", "/favicon.ico"):
        return True
    if path.startswith("/static/"):
        return True
    if path.startswith("/seller-cabinet"):
        return True
    if path == "/admin/login":
        return True
    return False


def safe_next_url(raw: str | None, default: str) -> str:
    """Только относительные пути, без open-redirect."""
    if not raw or not isinstance(raw, str):
        return default
    s = raw.strip()
    if not s.startswith("/") or s.startswith("//"):
        return default
    return s


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    В app.add_middleware: сначала SessionMiddleware, затем этот класс
    (Session снаружи — сессия уже есть, когда запрос доходит сюда).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        if _is_public_path(path):
            return await call_next(request)

        if request.session.get(ADMIN_SESSION_KEY):
            return await call_next(request)

        # POST /admin/logout без сессии — пусть обработчик сам редиректит
        if path == "/admin/logout":
            return await call_next(request)

        next_path = path
        if request.url.query:
            next_path = f"{path}?{request.url.query}"
        login_url = f"/admin/login?next={quote(next_path, safe='')}"

        if request.method in ("GET", "HEAD"):
            return RedirectResponse(url=login_url, status_code=303)

        # POST/PUT/DELETE без сессии — редирект на вход (данные формы потеряются)
        return RedirectResponse(url=login_url, status_code=303)
