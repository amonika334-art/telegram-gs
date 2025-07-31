import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import os

TOKEN = os.getenv("BOT_TOKEN")

# --- Налаштування прав ---
ALLOWED_USERS = {
    "чат": [],  # Сюди ID користувачів, яким дозволено писати в гілку "чат"
    "аналітика": [],  # інші гілки за потреби
}

DELETE_TIMEOUTS = {
    "чат": timedelta(days=2),
    "аналітика": timedelta(weeks=1)
}

# --- Логування ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Обробник /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я чат-бот контролю. Напиши /допомога")

# --- Обробник /допомога ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/дозвіл [гілка] [user_id] — дозволити користувачу писати в гілку
"
        "/очищення [гілка] [кількість_днів|тижнів] — встановити автоочищення
"
    )

# --- Обробка дозволу ---
async def allow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Формат: /дозвіл [гілка] [user_id]")
        return
    thread, user_id = context.args
    if thread not in ALLOWED_USERS:
        await update.message.reply_text("Невідома гілка.")
        return
    ALLOWED_USERS[thread].append(int(user_id))
    await update.message.reply_text(f"Користувачу {user_id} дозволено писати в гілку {thread}.")

# --- Обробка автоочищення ---
async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Формат: /очищення [гілка] [час]")
        return
    thread, time = context.args
    if "тиж" in time:
        days = int(time.split("тиж")[0]) * 7
    else:
        days = int(time)
    DELETE_TIMEOUTS[thread] = timedelta(days=days)
    await update.message.reply_text(f"Очищення гілки {thread} встановлено на {days} днів.")

# --- Обробка повідомлень ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    thread = msg.message_thread_id or "чат"  # За замовчуванням - гілка "чат"
    user_id = msg.from_user.id

    thread_str = "чат"  # Можна додати логіку для відповідності ID гілці
    allowed = ALLOWED_USERS.get(thread_str, [])

    if allowed and user_id not in allowed:
        try:
            await msg.delete()
        except:
            pass
        return

    timeout = DELETE_TIMEOUTS.get(thread_str)
    if timeout:
        await asyncio.sleep(timeout.total_seconds())
        try:
            await msg.delete()
        except:
            pass

# --- Запуск бота ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("допомога", help_command))
    app.add_handler(CommandHandler("дозвіл", allow_command))
    app.add_handler(CommandHandler("очищення", clean_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
