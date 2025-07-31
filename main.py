import asyncio
import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

SETTINGS_FILE = "settings.json"

# Завантаження налаштувань
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"permissions": {}, "autodelete": {}}

# Збереження налаштувань
def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

settings = load_settings()

# Перевірка чи користувач — адміністратор
async def is_admin(update: Update):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await update.get_bot().get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]

# Команда /дозволити
async def дозволити(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if len(context.args) != 3 or context.args[1] != "в":
        await update.message.reply_text("Приклад: /дозволити @user в чат")
        return
    user = context.args[0]
    topic = context.args[2].lower()
    settings["permissions"].setdefault(topic, [])
    if user not in settings["permissions"][topic]:
        settings["permissions"][topic].append(user)
        save_settings(settings)
    await update.message.reply_text(f"✅ {user} може писати в темі {topic}")

# Команда /заборонити
async def заборонити(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if len(context.args) != 3 or context.args[1] != "в":
        await update.message.reply_text("Приклад: /заборонити @user в чат")
        return
    user = context.args[0]
    topic = context.args[2].lower()
    if topic in settings["permissions"] and user in settings["permissions"][topic]:
        settings["permissions"][topic].remove(user)
        save_settings(settings)
    await update.message.reply_text(f"🚫 {user} більше не може писати в темі {topic}")

# Команда /автовидалення
async def автовидалення(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update): return
    if len(context.args) != 2:
        await update.message.reply_text("Приклад: /автовидалення чат 2д або /автовидалення чат викл")
        return
    topic = context.args[0].lower()
    val = context.args[1]
    if val == "викл":
        settings["autodelete"].pop(topic, None)
        save_settings(settings)
        await update.message.reply_text(f"🛑 Автовидалення для теми {topic} вимкнено")
    else:
        if val.endswith("д"):
            seconds = int(val[:-1]) * 86400
        elif val.endswith("т"):
            seconds = int(val[:-1]) * 604800
        else:
            await update.message.reply_text("⚠️ Вкажіть кількість днів (2д) або тижнів (1т)")
            return
        settings["autodelete"][topic] = seconds
        save_settings(settings)
        await update.message.reply_text(f"⏱ Автовидалення в темі {topic} через {val}")

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    username = f"@{user.username}" if user.username else f"id:{user.id}"
    topic_id = str(message.message_thread_id) if message.message_thread_id else "default"

    # Автовидалення
    if topic_id in settings["autodelete"]:
        delay = settings["autodelete"][topic_id]
        await asyncio.sleep(delay)
        try: await message.delete()
        except: pass
        return

    # Перевірка дозволу
    if topic_id in settings["permissions"]:
        if username not in settings["permissions"][topic_id]:
            try: await message.delete()
            except: pass

# Запуск
async def main():
    from os import getenv
    token = getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("дозволити", дозволити))
    app.add_handler(CommandHandler("заборонити", заборонити))
    app.add_handler(CommandHandler("автовидалення", автовидалення))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
