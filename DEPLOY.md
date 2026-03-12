# Деплой бота учёта смен (shift_bot) на GitHub и Railway

## 1. GitHub

### Если репозитория ещё нет

```bash
cd /Users/ramazanmirzaev/telegram-expense-bot
git init
git add .
git commit -m "Shift bot: учёт смен и отчёты"
```

На GitHub создай новый репозиторий (без README), затем:

```bash
git remote add origin https://github.com/ТВОЙ_ЛОГИН/ИМЯ_РЕПОЗИТОРИЯ.git
git branch -M main
git push -u origin main
```

### Если репозиторий уже есть

```bash
cd /Users/ramazanmirzaev/telegram-expense-bot
git add .
git commit -m "Shift bot: деплой на Railway"
git push
```

---

## 2. Railway

1. Зайди на [railway.app](https://railway.app) и войди в аккаунт.
2. **New Project** → **Deploy from GitHub repo** → выбери репозиторий `telegram-expense-bot`.
3. Railway сам подхватит `Procfile` и `nixpacks.toml` из корня репозитория (запуск будет из папки `shift_bot`).
4. Открой созданный сервис → вкладка **Variables** и добавь:
   - `BOT_TOKEN` — токен бота от @BotFather.
   - `ADMIN_IDS` — твой Telegram ID (узнать: @userinfobot).
5. Сохрани переменные. Railway пересоберёт и перезапустит приложение.
6. Вкладка **Settings** → при необходимости включи **Public Networking** (для бота обычно не нужно).
7. Логи смотри во вкладке **Deployments** → выбери деплой → **View Logs**.

После деплоя открой бота в Telegram и отправь `/start`. С аккаунта из `ADMIN_IDS` отчёты будут приходить в чат с ботом.

---

**Важно:** На Railway по умолчанию используется SQLite внутри контейнера. При пересоздании контейнера данные обнуляются. Для постоянной базы добавь в проект сервис **PostgreSQL**, скопируй его `DATABASE_URL` в переменные и добавь переменную `DATABASE_URL` в настройки сервиса бота (формат см. в `shift_bot/README_RAILWAY.md`).
