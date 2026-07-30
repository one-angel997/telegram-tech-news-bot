import os
import asyncio
import feedparser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

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
        # Arresta l'applicazione subito dopo aver risposto
        await asyncio.sleep(0.3)
        try:
            await context.application.stop()
        except TypeError:
            context.application.stop()
        return

    # Limitiamo il numero totale di notizie
    risposta = "\n\n".join(news_list[:15])
    
    # Crea il pulsante anche nel messaggio delle notizie
    keyboard = [
        [InlineKeyboardButton("🔄 Ricerca di nuovo", callback_data="get_tech")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.effective_message.reply_text("📰 Ecco le ultime news:\n\n" + risposta, reply_markup=reply_markup)

    # Dopo aver inviato le notizie, fermiamo l'applicazione per "auto-distruzione"
    await asyncio.sleep(0.5)  # piccolo ritardo per essere sicuri che i messaggi siano inviati
    try:
        await context.application.stop()
    except TypeError:
        context.application.stop()


async def tech_button_callback(update, context):
    """Gestisce il click del pulsante e chiama la funzione tech"""
    query = update.callback_query
    await query.answer()  # Chiude la notifica di caricamento
    
    # Chiama direttamente la funzione tech
    await tech(update, context)


def main():
    if not TOKEN or TOKEN == "INSERISCI_IL_TUO_TOKEN_TELEGRAM":
        raise ValueError("Devi impostare il TOKEN del bot Telegram in bot.py o nella variabile TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CallbackQueryHandler(tech_button_callback, pattern="get_tech"))

    app.run_polling()


if __name__ == "__main__":
    main()
