import os

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from app.common.config import get_config
from app.telegram.handlers import start, list_news, summary_callback


def main():
    config = get_config()
    token = config.get("bot", {}).get("token") or os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN non impostato. Controlla .env del profilo.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", lambda update, context: list_news(update, context, "all")))
    app.add_handler(CommandHandler("f1", lambda update, context: list_news(update, context, "all")))
    app.add_handler(
        CallbackQueryHandler(
            lambda update, context: list_news(
                update,
                context,
                update.callback_query.data.removeprefix("category:"),
            ),
            pattern=r"^category:"
        )
    )
    app.add_handler(CallbackQueryHandler(summary_callback, pattern=r"^get_summary:"))

    app.run_polling()
