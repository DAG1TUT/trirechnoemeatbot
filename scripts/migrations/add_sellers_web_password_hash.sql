-- Одноразово для существующей PostgreSQL: колонка для веб-кабинета продавца.
-- После применения перезапуск приложения не обязателен.

ALTER TABLE sellers
  ADD COLUMN IF NOT EXISTS web_password_hash VARCHAR(255);
