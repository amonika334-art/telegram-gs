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

# Дозволені user_id (адміністратори)
ALLOWED_USER_IDS = [309352555]  # ← твій Telegram ID
RESTRICTED_TOPICS = {"admin", "only-admins"}  # теми, куди звичайним користувачам не можна писати
AUTO_CLEAN_TOPICS = {
    "chat": 60 * 60 * 24 * 7  # автозачищення через 7 днів
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Це Telegram бот з контролем доступу та автоочищенням.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    topic = message.message_thread_id

    if topic:
        topic_title = (await context.bot.get_forum_topic(
            chat_id=message.chat_id,
            message_thread_id=topic
        )).name.lower()

        # якщо тема обмежена і користувач не має прав
        if topic_title in RESTRICTED_TOPICS and user_id not in ALLOWED_USER_IDS:
            await message.delete()
            return

        # якщо тема потребує автоочищення
        if topic_title in AUTO_CLEAN_TOPICS:
            delete_after = AUTO_CLEAN_TOPICS[topic_title]
            context.job_queue.run_once(
                lambda ctx: ctx.bot.delete_message(
                    chat_id=message.chat_id,
                    message_id=message.message_id
                ),
                when=delete_after,
                name=f"auto-delete-{message.message_id}"
            )


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

