# -*- coding: utf-8 -*-
"""
Telegram-бот для учёта расходов с автоматической категоризацией.
Запуск: python bot.py
"""

import re
import os
import tempfile
from datetime import datetime
from typing import Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

import database as db
from categories import detect_category, get_all_categories
from google_sheets import append_expense_to_sheet

# Голосовые сообщения (опционально)
try:
    import speech_recognition as sr
    from pydub import AudioSegment

    # На Mac при запуске из Cursor/терминала PATH может не содержать Homebrew — добавляем вручную
    _brew_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
    for _p in _brew_paths:
        if os.path.isdir(_p):
            _ffmpeg = os.path.join(_p, "ffmpeg")
            _ffprobe = os.path.join(_p, "ffprobe")
            if os.path.isfile(_ffmpeg) and os.path.isfile(_ffprobe):
                AudioSegment.converter = _ffmpeg
                # pydub ищет ffprobe через which() — добавляем путь в PATH
                _path = os.environ.get("PATH", "")
                if _p not in _path:
                    os.environ["PATH"] = _p + os.pathsep + _path
                break
    VOICE_AVAILABLE = True
except ImportError as e:
    # Логируем причину отключения голоса (полезно на Railway)
    print(f"VOICE_DISABLED_IMPORT_ERROR: {e}")
    VOICE_AVAILABLE = False


def _replace_russian_amounts(text: str) -> str:
    """Заменяет русские числительные на цифры: «две с половиной тысячи» -> 2500."""
    t = text.lower()
    # Порядок важен: сначала длинные фразы
    replacements = [
        (r"две\s+с\s+половиной\s+тысяч[иеёауы]?", "2500"),
        (r"два\s+с\s+половиной\s+тысяч[иеёауы]?", "2500"),
        (r"две\s+с\s+половиной\s+тыщ", "2500"),   # разг. «тыщи»
        (r"полторы?\s+тысяч[иеёауы]?", "1500"),
        (r"(\d+)\s*[,.]?\s*5\s+тысяч", lambda m: str(int(m.group(1)) * 1000 + 500)),  # 2.5 тысячу -> 2500
        (r"две\s+тысячи", "2000"),
        (r"два\s+тысячи", "2000"),
        (r"пять\s+тысяч", "5000"),
        (r"три\s+тысячи", "3000"),
        (r"четыре\s+тысячи", "4000"),
        (r"одна\s+тысяча", "1000"),
        (r"одну\s+тысячу", "1000"),
        (r"тысяча\s+руб", "1000"),
        (r"(\d+)\s+тысяч", lambda m: str(int(m.group(1)) * 1000)),  # 3 тысяч -> 3000
        (r"(\d+)\s+тысячи", lambda m: str(int(m.group(1)) * 1000)),
        (r"пятьсот", "500"),
        (r"шестьсот", "600"),
        (r"семьсот", "700"),
        (r"восемьсот", "800"),
        (r"девятьсот", "900"),
        (r"триста", "300"),
        (r"четыреста", "400"),
        (r"двести", "200"),
        (r"сто\s+руб", "100"),
        (r"сто\s+$", "100"),
        (r"двести\s+пятьдесят", "250"),
        (r"триста\s+пятьдесят", "350"),
        (r"пятьдесят", "50"),
        (r"сорок", "40"),
        (r"тридцать", "30"),
        (r"двадцать", "20"),
        (r"десять", "10"),
    ]
    for pattern, repl in replacements:
        if callable(repl):
            t = re.sub(pattern, repl, t, flags=re.I)
        else:
            t = re.sub(pattern, " " + repl + " ", t, flags=re.I)
    return t


def parse_expense_message(text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Парсит сообщение вида "кофе 500", "500 руб на обед", "две с половиной тысячи на заправку" и т.д.
    Возвращает (сумма, описание) или (None, None) при ошибке.
    """
    text = text.strip()
    if not text:
        return None, None

    # Убираем валюты и лишние слова для поиска числа
    normalized = re.sub(r'\s*(руб|рублей|р\.|р\s|₽|тенге|тг|usd|\$|eur|€)\s*', ' ', text, flags=re.I)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    # Русские числительные («две с половиной тысячи», «пятьсот») -> цифры
    normalized = _replace_russian_amounts(normalized)

    # Ищем число: целое или с запятой/точкой
    num_pattern = r'(?:\d[\d\s]*)(?:[.,]\d+)?|\d+'
    matches = list(re.finditer(num_pattern, normalized))

    if not matches:
        return None, None

    # Берём самое длинное число (чаще всего это сумма)
    best_match = max(matches, key=lambda m: len(m.group().replace(' ', '')))
    num_str = best_match.group().replace(' ', '').replace(',', '.')
    try:
        amount = float(num_str)
    except ValueError:
        return None, None
    if amount <= 0:
        return None, None

    # Описание — всё остальное без этого числа
    before = normalized[: best_match.start()].strip()
    after = normalized[best_match.end() :].strip()
    parts = [p for p in (before, after) if p]
    description = ' '.join(parts) if parts else str(amount)

    # Если описание пустое — используем "трата" или саму сумму как подсказку
    if not description or description.replace('.', '').replace(',', '').isdigit():
        description = "трата"

    # Голос часто даёт только «две» вместо «две с половиной тысячи» — по смыслу подставляем тысячи
    small_amounts = (1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10)
    thousands_keywords = ("заправ", "машин", "бензин", "тысяч", "тыщ", "аренд", "квартир", "ипотек", "коммуналк", "ремонт", "техник", "телефон", "ноутбук", "продукт")
    desc_lower = (description + " " + text).lower()
    if amount in small_amounts and any(kw in desc_lower for kw in thousands_keywords):
        amount = amount * 1000

    return amount, description


# Тексты кнопок (должны совпадать с клавиатурой)
BTN_TOTAL = "📊 Общие траты"
BTN_CATS = "📁 По категориям"
BTN_LIST = "📋 Последние траты"
BTN_RESET = "♻️ Сбросить расходы"

def _main_menu_keyboard():
    """Инлайн-кнопки под сообщением."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BTN_TOTAL, callback_data="btn_total")],
        [InlineKeyboardButton(BTN_CATS, callback_data="btn_cats")],
        [InlineKeyboardButton(BTN_LIST, callback_data="btn_list")],
    ])


def _reply_keyboard():
    """Постоянная клавиатура внизу экрана (всегда видна)."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_TOTAL), KeyboardButton(BTN_LIST)],
            [KeyboardButton(BTN_CATS)],
            [KeyboardButton(BTN_RESET)],
        ],
        resize_keyboard=True,
    )


def _expenses_list_message(user_id: int, limit: int = 10):
    """Текст и клавиатура для «Последние траты» с кнопками Удалить / Изменить категорию."""
    rows = db.get_expenses(user_id, limit=limit)
    if not rows:
        return "Пока нет записей о расходах.", None
    lines = ["Последние траты (нажми ✏️ или 🗑):\n"]
    buttons = []
    for r in rows:
        date = r["created_at"][:10] if r.get("created_at") else ""
        lines.append(f"• {r['amount']:,.0f} ₽ — {r['description']} [{r['category']}] {date}")
        eid = r["id"]
        buttons.append([
            InlineKeyboardButton("✏️", callback_data=f"edit_{eid}"),
            InlineKeyboardButton("🗑", callback_data=f"del_{eid}"),
        ])
    buttons.append([InlineKeyboardButton("← Меню", callback_data="btn_menu")])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Клавиатура внизу экрана — кнопки всегда видны
    await update.message.reply_text(
        "Привет! Я бот для учёта расходов.\n\n"
        "Напиши или запиши голосом, на что и сколько потратил, например: кофе 350 или «пятьсот на обед».\n"
        "Или нажми кнопку внизу:",
        reply_markup=_reply_keyboard(),
    )


def _format_total_and_by_category(user_id: int, period_days: int = 30):
    """Общие траты за период и разбивка по категориям."""
    rows = db.get_summary_by_category(user_id, period_days=period_days)
    if not rows:
        return None
    total = sum(r["total"] for r in rows)
    lines = [f"📊 Общие траты за {period_days} дн.: {total:,.0f} ₽\n"]
    lines.append("По категориям:")
    for r in rows:
        pct = (r["total"] / total * 100) if total else 0
        lines.append(f"  {r['category']}: {r['total']:,.0f} ₽ ({pct:.0f}%)")
    return "\n".join(lines)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = _format_total_and_by_category(user_id, period_days=30)
    if not text:
        await update.message.reply_text("Пока нет трат за последние 30 дней.")
        return
    await update.message.reply_text(text)


async def _cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать кнопки меню."""
    await update.message.reply_text("Выбери действие:", reply_markup=_reply_keyboard())


async def cmd_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Общие траты + по категориям (то же, что /stats)."""
    user_id = update.effective_user.id
    text = _format_total_and_by_category(user_id, period_days=30)
    if not text:
        await update.message.reply_text("Пока нет трат за последние 30 дней.")
        return
    await update.message.reply_text(text)


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text, kb = _expenses_list_message(user_id, limit=10)
    if kb:
        await update.message.reply_text(text, reply_markup=kb)
    else:
        await update.message.reply_text(text)


async def cmd_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    total = db.get_total(user_id, period_days=30)
    await update.message.reply_text(f"За последние 30 дней потрачено: {total:,.0f} ₽")


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос на полное удаление всех трат пользователя (с подтверждением)."""
    user_id = update.effective_user.id
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Да, удалить все мои траты", callback_data="reset_confirm"),
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="reset_cancel"),
        ],
    ])
    await update.message.reply_text(
        "Точно удалить **все** твои траты из бота? Это действие нельзя отменить.",
        reply_markup=kb,
        parse_mode="Markdown",
    )


async def cmd_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Траты по одной категории: /cat еда или /cat транспорт."""
    user_id = update.effective_user.id
    args = (context.args or [])
    if not args:
        categories = db.get_category_totals(user_id, period_days=30)
        if not categories:
            await update.message.reply_text("Пока нет трат. Укажи категорию, например: /cat еда")
            return
        lines = ["Напиши /cat и слово из категории, например:\n"]
        for r in categories[:10]:
            lines.append(f"  {r['category']} — {r['total']:,.0f} ₽")
        lines.append("\nПример: /cat еда или /cat транспорт")
        await update.message.reply_text("\n".join(lines))
        return
    query = " ".join(args).strip().lower()
    expenses = db.get_expenses_by_category(user_id, query, period_days=30, limit=40)
    if not expenses:
        await update.message.reply_text(f"По категории «{query}» трат за 30 дней нет.")
        return
    total_cat = sum(e["amount"] for e in expenses)
    lines = [f"📁 Траты по категории («{query}»), 30 дн.: {total_cat:,.0f} ₽\n"]
    for e in expenses[:25]:
        date = e["created_at"][:10] if e.get("created_at") else ""
        lines.append(f"  • {e['amount']:,.0f} ₽ — {e['description']} ({date})")
    if len(expenses) > 25:
        lines.append(f"  … и ещё {len(expenses) - 25}")
    await update.message.reply_text("\n".join(lines))


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id if query.from_user else 0
    data = query.data or ""

    if data == "btn_total":
        text = _format_total_and_by_category(user_id, period_days=30)
        if not text:
            text = "Пока нет трат за последние 30 дней."
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("← Меню", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=kb)

    elif data == "btn_list":
        text, kb = _expenses_list_message(user_id, limit=10)
        if not kb:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("← Меню", callback_data="btn_menu")]])
        await query.edit_message_text(text=text, reply_markup=kb)

    elif data == "btn_cats":
        # Показываем все категории из списка, а не только те, по которым есть траты
        all_cats = get_all_categories()
        summary = db.get_summary_by_category(user_id, period_days=30)
        totals = {r["category"]: r["total"] for r in summary}
        buttons = []
        row = []
        for i, cat in enumerate(all_cats[:18]):
            total = totals.get(cat, 0)
            label = f"{cat} — {total:,.0f} ₽"
            if len(label) > 35:
                label = cat[:32] + "…"
            row.append(InlineKeyboardButton(label, callback_data=f"cat_{i}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton("← Меню", callback_data="btn_menu")])
        await query.edit_message_text(
            "Выбери категорию (30 дней):",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif data == "btn_menu":
        await query.edit_message_text(
            "Выбери действие:",
            reply_markup=_main_menu_keyboard(),
        )

    elif data.startswith("cat_"):
        try:
            idx = int(data.replace("cat_", ""))
        except ValueError:
            await query.answer("Ошибка")
            return
        all_cats = get_all_categories()
        if idx < 0 or idx >= len(all_cats):
            await query.answer("Категория не найдена")
            return
        category_name = all_cats[idx]
        expenses = db.get_expenses_by_category(user_id, category_name, period_days=30, limit=40)
        if not expenses:
            text = f"По категории {category_name} трат за 30 дней нет."
        else:
            total_cat = sum(e["amount"] for e in expenses)
            lines = [f"📁 {category_name}\n30 дн.: {total_cat:,.0f} ₽\n"]
            for e in expenses[:20]:
                date = e["created_at"][:10] if e.get("created_at") else ""
                lines.append(f"  • {e['amount']:,.0f} ₽ — {e['description']} ({date})")
            if len(expenses) > 20:
                lines.append(f"  … и ещё {len(expenses) - 20}")
            text = "\n".join(lines)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("← К категориям", callback_data="btn_cats")],
            [InlineKeyboardButton("← Меню", callback_data="btn_menu")],
        ])
        await query.edit_message_text(text=text, reply_markup=kb)

    elif data.startswith("del_"):
        try:
            expense_id = int(data.replace("del_", ""))
        except ValueError:
            await query.answer("Ошибка")
            return
        if db.delete_expense(user_id, expense_id):
            await query.answer("Трата удалена")
            text, kb = _expenses_list_message(user_id, limit=10)
            if not kb:
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("← Меню", callback_data="btn_menu")]])
            await query.edit_message_text(text=text, reply_markup=kb)
        else:
            await query.answer("Трата не найдена")

    elif data.startswith("edit_"):
        try:
            expense_id = int(data.replace("edit_", ""))
        except ValueError:
            await query.answer("Ошибка")
            return
        exp = db.get_expense_by_id(user_id, expense_id)
        if not exp:
            await query.answer("Трата не найдена")
            return
        await query.answer()
        label = f"{exp['amount']:,.0f} ₽ — {exp['description']}"
        all_cats = get_all_categories()
        buttons = []
        row = []
        for i, cat in enumerate(all_cats):
            row.append(InlineKeyboardButton(cat, callback_data=f"setcat_{expense_id}_{i}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton("← К списку", callback_data="btn_list")])
        await query.edit_message_text(
            f"Выбери новую категорию для траты:\n{label}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif data.startswith("setcat_"):
        parts = data.split("_")
        if len(parts) != 3:
            await query.answer("Ошибка")
            return
        try:
            expense_id = int(parts[1])
            cat_idx = int(parts[2])
        except ValueError:
            await query.answer("Ошибка")
            return
        all_cats = get_all_categories()
        if cat_idx < 0 or cat_idx >= len(all_cats):
            await query.answer("Категория не найдена")
            return
        new_cat = all_cats[cat_idx]
        exp = db.get_expense_by_id(user_id, expense_id)
        if not exp:
            await query.answer("Трата не найдена")
            return
        if db.update_expense_category(user_id, expense_id, new_cat):
            await query.answer(f"Категория изменена на {new_cat}")
            label = f"{exp['amount']:,.0f} ₽ — {exp['description']}"
            await query.edit_message_text(
                f"✅ Категория изменена.\n{label}\n→ {new_cat}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("← К списку трат", callback_data="btn_list")],
                    [InlineKeyboardButton("← Меню", callback_data="btn_menu")],
                ]),
            )
        else:
            await query.answer("Не удалось изменить")

    elif data == "reset_confirm":
        deleted = db.delete_all_expenses(user_id)
        text = (
            "Все твои траты удалены из бота."
            if deleted
            else "У тебя и так нет сохранённых трат."
        )
        await query.edit_message_text(
            text,
            reply_markup=_main_menu_keyboard(),
        )

    elif data == "reset_cancel":
        await query.edit_message_text(
            "Удаление отменено.",
            reply_markup=_main_menu_keyboard(),
        )


async def _send_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE, button_data: str):
    """Ответ на нажатие кнопки меню (когда нажали Reply-клавиатуру)."""
    user_id = update.effective_user.id
    msg = update.message.reply_text
    if button_data == "btn_total":
        text = _format_total_and_by_category(user_id, period_days=30)
        await msg(text or "Пока нет трат за последние 30 дней.")
    elif button_data == "btn_list":
        text, kb = _expenses_list_message(user_id, limit=10)
        if kb:
            await msg(text, reply_markup=kb)
        else:
            await msg(text)
    elif button_data == "btn_cats":
        all_cats = get_all_categories()
        summary = db.get_summary_by_category(user_id, period_days=30)
        totals = {r["category"]: r["total"] for r in summary}
        buttons = []
        row = []
        for i, cat in enumerate(all_cats[:18]):
            total = totals.get(cat, 0)
            label = f"{cat} — {total:,.0f} ₽"
            if len(label) > 35:
                label = cat[:32] + "…"
            row.append(InlineKeyboardButton(label, callback_data=f"cat_{i}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton("← Меню", callback_data="btn_menu")])
        await msg("Выбери категорию (30 дней):", reply_markup=InlineKeyboardMarkup(buttons))
    elif button_data == "btn_reset":
        # Используем ту же логику, что и команда /reset
        await cmd_reset(update, context)


def _voice_to_text(ogg_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Конвертирует голосовой ogg/opus в текст (русский). Возвращает (текст, ошибка)."""
    if not VOICE_AVAILABLE:
        return None, "нет библиотек (SpeechRecognition, pydub)"
    wav_path = None
    try:
        # Telegram присылает ogg/opus — пусть ffmpeg сам определит формат
        try:
            audio = AudioSegment.from_file(ogg_path)
        except Exception as e:
            return None, f"конвертация в аудио: {e}. Установи ffmpeg: brew install ffmpeg"
        if len(audio) == 0:
            return None, "пустой аудиофайл"
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            audio.export(wav_path, format="wav")
            rec = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                rec.adjust_for_ambient_noise(source, duration=0.3)
                data = rec.record(source)
            text = rec.recognize_google(data, language="ru-RU")
            return (text.strip() if text else None), None
        except sr.UnknownValueError:
            return None, "речь не распознана (скажи чётче: «пятьсот на кофе»)"
        except sr.RequestError as e:
            return None, f"ошибка сервиса распознавания (интернет?): {e}"
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                except OSError:
                    pass
    except Exception as e:
        return None, str(e)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Распознавание голосового сообщения и запись траты."""
    if not VOICE_AVAILABLE:
        await update.message.reply_text(
            "Голосовые сообщения пока не поддерживаются. Установи: pip3 install SpeechRecognition pydub. Нужен ffmpeg."
        )
        return
    voice = update.message.voice
    if not voice or not voice.file_id:
        await update.message.reply_text("Не удалось получить голосовое сообщение.")
        return
    await update.message.reply_text("Обрабатываю голос…")
    ogg_path = None
    try:
        file = await context.bot.get_file(voice.file_id)
        fd, ogg_path = tempfile.mkstemp(suffix=".ogg")
        os.close(fd)
        try:
            await file.download_to_drive(ogg_path)
            if os.path.getsize(ogg_path) == 0:
                await update.message.reply_text("Ошибка: файл голоса пустой.")
                return
            text, err = _voice_to_text(ogg_path)
        finally:
            if ogg_path and os.path.exists(ogg_path):
                try:
                    os.unlink(ogg_path)
                except OSError:
                    pass
    except Exception as e:
        await update.message.reply_text(f"Ошибка загрузки: {e}")
        return
    if err:
        await update.message.reply_text(f"Не удалось распознать: {err}")
        return
    if not text:
        await update.message.reply_text(
            "Речь не распознана. Скажи чётко, например: «пятьсот рублей на кофе»."
        )
        return
    amount, description = parse_expense_message(text)
    if amount is None:
        await update.message.reply_text(
            f"Распознано: «{text}». Не удалось извлечь сумму и описание. Напиши текстом, например: кофе 500"
        )
        return
    user_id = update.effective_user.id
    category = detect_category(description)
    created_at = db.add_expense(user_id, amount, description, category, datetime.now().isoformat())
    append_expense_to_sheet(user_id, amount, description, category, created_at)
    await update.message.reply_text(
        f"Записал по голосу: {amount:,.0f} ₽ — {description}\nКатегория: {category}"
    )


async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    # Нажатие кнопки меню (Reply-клавиатура)
    if text == BTN_TOTAL:
        await _send_menu_response(update, context, "btn_total")
        return
    if text == BTN_LIST:
        await _send_menu_response(update, context, "btn_list")
        return
    if text == BTN_CATS:
        await _send_menu_response(update, context, "btn_cats")
        return
    if text == BTN_RESET:
        await _send_menu_response(update, context, "btn_reset")
        return

    amount, description = parse_expense_message(text)
    if amount is None:
        await update.message.reply_text(
            "Не понял. Напиши, например: кофе 500 или 2000 продукты"
        )
        return

    category = detect_category(description)
    created_at = db.add_expense(user_id, amount, description, category, datetime.now().isoformat())
    append_expense_to_sheet(user_id, amount, description, category, created_at)
    await update.message.reply_text(
        f"Записал: {amount:,.0f} ₽ — {description}\nКатегория: {category}"
    )


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Задайте переменную окружения TELEGRAM_BOT_TOKEN.")
        return
    db.init_db()
    # Проверка Google Sheets при старте
    try:
        from google_sheets import _get_sheet
        if _get_sheet() is not None:
            print("Google Sheets: подключено, траты записываются в таблицу.", flush=True)
        else:
            print("Google Sheets: не настроено. Задайте GOOGLE_SHEETS_CREDS_JSON и GOOGLE_SHEETS_SPREADSHEET_ID в Variables.", flush=True)
    except Exception as e:
        print(f"Google Sheets: ошибка — {e}", flush=True)
    # Не использовать системный прокси (избегаем 403 при корпоративном/системном прокси)
    request = HTTPXRequest(proxy=None, httpx_kwargs={"trust_env": False})
    app = Application.builder().token(token).request(request).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("total", cmd_total))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("month", cmd_month))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("cat", cmd_category))
    app.add_handler(CommandHandler("menu", _cmd_menu))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense))
    print("Бот запущен.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
