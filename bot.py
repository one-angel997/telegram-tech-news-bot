import os
import feedparser
from telegram.ext import ApplicationBuilder, CommandHandler

# Puoi usare una variabile d'ambiente oppure scrivere il token in chiaro
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "INSERISCI_IL_TUO_TOKEN_TELEGRAM")

# Fonti italiane di news tech
FEEDS = [
    "https://www.hdblog.it/rss/",
    "https://www.smartworld.it/feed",
    "https://rss.hwupgrade.it/news.xml",
    "https://www.tomshw.it/feed/",
    "https://www.everyeye.it/feed/notizie/",
    "https://www.wired.it/feed/tech/"
]


async def start(update, context):
    await update.message.reply_text(
        "Ciao! 👋\n"
        "Sono il tuo bot per le notizie tech italiane.\n"
        "Usa /tech per vedere le ultime novità."
    )


async def tech(update, context):
    await update.message.reply_text("🔍 Recupero le ultime notizie tech italiane...")

    news_list = []

    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # 3 notizie per fonte
            title = entry.title
            link = entry.link
            news_list.append(f"• {title}\n{link}")

    if not news_list:
        await update.message.reply_text("Nessuna notizia trovata al momento.")
        return

    # Limitiamo il numero totale di notizie
    risposta = "\n\n".join(news_list[:15])
    await update.message.reply_text("📰 Ecco le ultime news:\n\n" + risposta)


def main():
    if not TOKEN or TOKEN == "INSERISCI_IL_TUO_TOKEN_TELEGRAM":
        raise ValueError("Devi impostare il TOKEN del bot Telegram in bot.py o nella variabile TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", tech))

    app.run_polling()


if __name__ == "__main__":
    main()
