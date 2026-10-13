import os
import feedparser
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Carica il token dal file .env presente nella cartella del progetto
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Devi impostare TELEGRAM_BOT_TOKEN nel file .env")

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
    # Crea il pulsante inline che chiama tech
    keyboard = [
        [InlineKeyboardButton("📰 Ultime Notizie Tech", callback_data="get_tech")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Ciao! 👋\n"
        "Sono il tuo bot per le notizie tech italiane.\n"
        "Clicca il pulsante sotto per vedere le ultime novità!",
        reply_markup=reply_markup
    )


async def tech(update, context):
    # Usa effective_message per funzionare sia con comandi che con callback
    await update.effective_message.reply_text("🔍 Recupero le ultime notizie tech italiane...")

    news_list = []

    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # 3 notizie per fonte
            title = entry.title
            link = entry.link
            news_list.append(f"• {title}\n{link}")

    if not news_list:
        await update.effective_message.reply_text("Nessuna notizia trovata al momento.")
        return

    # Limitiamo il numero totale di notizie
    risposta = "\n\n".join(news_list[:15])
    
    # Crea il pulsante anche nel messaggio delle notizie
    keyboard = [
        [InlineKeyboardButton("🔄 Ricerca di nuovo", callback_data="get_tech")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.effective_message.reply_text("📰 Ecco le ultime news:\n\n" + risposta, reply_markup=reply_markup)


async def tech_button_callback(update, context):
    """Gestisce il click del pulsante e chiama la funzione tech"""
    query = update.callback_query
    await query.answer()  # Chiude la notifica di caricamento
    
    # Chiama direttamente la funzione tech
    await tech(update, context)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CallbackQueryHandler(tech_button_callback, pattern="get_tech"))

    app.run_polling()


if __name__ == "__main__":
    main()
