
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👤 Дозволені користувачі для кожної гілки
ALLOWED_USERS = {
    "чат": [123456789],       # 🔁 заміни на справжній user_id
    "тех": [987654321],       # 🔁 заміни на справжній user_id
    "новини": []
}

# 🧹 Конфіг автоочищення повідомлень
AUTO_CLEAN_CONFIG = {
    "чат": {"days": 1},
    "новини": {"weeks": 1}
}

# 🔧 Логи
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Вітаю! Я бот для керування гілками Telegram.")

# ❓ Допомога
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Команди:\n"
        "/start — запустити бота\n"
        "/help — допомога\n"
        "/додай_гілку [назва] — додати нову гілку\n"
        "/очищення [назва] [днів|тижнів] [кількість] — автоочищення повідомлень"
    )

# ⛔ Невідома команда
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Невідома команда. Напишіть /help для списку доступних.")

# ➕ Додати гілку
async def додай_гілку(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("✏️ Вкажіть назву гілки. Наприклад: /додай_гілку чат")
        return

    branch = context.args[0].lower()
    if branch in ALLOWED_USERS:
        await update.message.reply_text(f"⚠️ Гілка '{branch}' вже існує.")
    else:
        ALLOWED_USERS[branch] = [update.message.from_user.id]
        await update.message.reply_text(f"✅ Гілка '{branch}' додана для {update.message.from_user.first_name}.")

# 🧼 Автоочищення
async def очищення(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        branch = context.args[0].lower()
        unit = context.args[1]
        amount = int(context.args[2])

        if unit not in ("днів", "тижнів"):
            raise ValueError()

        config = {"days": amount} if unit == "днів" else {"weeks": amount}
        AUTO_CLEAN_CONFIG[branch] = config

        await update.message.reply_text(f"✅ Очищення для гілки '{branch}' встановлено на {amount} {unit}.")

    except Exception:
        await update.message.reply_text("❌ Синтаксис: /очищення [назва] [днів|тижнів] [кількість]")

# ▶️ Запуск
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("додай_гілку", додай_гілку))
    app.add_handler(CommandHandler("очищення", очищення))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🤖 Бот запущено...")
    app.run_polling()

if __name__ == '__main__':
    main()
