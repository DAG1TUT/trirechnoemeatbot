# Миграции для PostgreSQL

## Зачем это

`init_db()` / `Base.metadata.create_all()` **создаёт только отсутствующие таблицы**.  
Если таблица `sellers` уже была, а в коде позже появилась колонка `web_password_hash`, **PostgreSQL сам её не добавит** — нужно выполнить SQL **один раз**.

## Что сделать на Railway (или любом Postgres)

### 1. Колонка для веб-кабинета продавца

Выполни в **Query** у PostgreSQL или через `psql`:

```sql
ALTER TABLE sellers
  ADD COLUMN IF NOT EXISTS web_password_hash VARCHAR(255);
```

Готовый файл: **`add_sellers_web_password_hash.sql`** (в этой папке).

### 2. Проверка

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'sellers'
  AND column_name = 'web_password_hash';
```

Должна быть **одна строка**.

### 3. Если колонка уже есть

Ничего делать не нужно — `IF NOT EXISTS` безопасен.

## Новые базы «с нуля»

Если БД создаётся **после** появления поля в модели и таблицы создаются через `create_all`, колонка может быть создана автоматически. Если сомневаешься — всё равно выполни SQL выше (не сломает).

## Дальше

При добавлении новых полей в модели — заводите сюда новый `.sql` и один раз выполняйте на проде (или подключите Alembic для автоматических миграций).
