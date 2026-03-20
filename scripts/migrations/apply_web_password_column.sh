#!/usr/bin/env bash
# Одноразово: добавить web_password_hash в sellers (PostgreSQL).
# Использование: из корня репозитория, с переменной DATABASE_URL:
#   export DATABASE_URL='postgresql://...'
#   bash scripts/migrations/apply_web_password_column.sh
#
# Для Railway: скопируй DATABASE_URL из Variables сервиса PostgreSQL или приложения.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SQL="$ROOT/scripts/migrations/add_sellers_web_password_hash.sql"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Задай DATABASE_URL (строка подключения к PostgreSQL)." >&2
  exit 1
fi

# psql понимает postgres:// и postgresql://
if ! command -v psql >/dev/null 2>&1; then
  echo "Нужен psql (PostgreSQL client). На Mac: brew install libpq && brew link --force libpq" >&2
  exit 1
fi

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$SQL"
echo "OK: миграция add_sellers_web_password_hash применена."
