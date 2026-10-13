import os
import re
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

CATEGORIES = {
    "smartphone": {
        "label": "📱 Smartphone e cellulari",
        "keywords": ("smartphone", "cellulare", "iphone", "android", "samsung galaxy", "xiaomi", "pixel phone"),
    },
    "pc": {
        "label": "💻 PC e laptop",
        "keywords": ("laptop", "notebook", "pc", "computer", "processore", "scheda video", "gpu", "desktop", "macbook"),
    },
    "ai": {
        "label": "🤖 AI e affini",
        "keywords": ("ai", "intelligenza artificiale", "machine learning", "deep learning", "generative ai", "chatgpt", "openai", "gemini", "copilot", "llm", " ia "),
    },
    "telecom": {
        "label": "📶 Telecomunicazioni",
        "keywords": ("telecomunicazioni", "5g", "6g", "fibra ottica", "banda larga", "wifi", "wi-fi", "rete mobile", "operatore telefonico", "starlink"),
    },
    "informatica": {
        "label": "🖥 Informatica",
        "keywords": ("software", "cybersecurity", "sicurezza informatica", "database", "cloud", "windows", "linux", "applicazione", "programmazione", "internet", "videogioco"),
    },
}


def matches_category(entry, category_id):
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".casefold()
    for keyword in CATEGORIES[category_id]["keywords"]:
        keyword = keyword.strip()
        if len(keyword) <= 3:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                return True
        elif keyword in text:
            return True
    return False


def category_keyboard():
    category_ids = list(CATEGORIES)
    rows = [
        [InlineKeyboardButton(CATEGORIES[category_id]["label"], callback_data=f"category:{category_id}")
         for category_id in category_ids[index:index + 2]]
        for index in range(0, len(category_ids), 2)
    ]
    rows.append([InlineKeyboardButton("📰 Tutte le notizie", callback_data="category:all")])
    return InlineKeyboardMarkup(rows)


async def start(update, context):
    await update.message.reply_text(
        "Ciao! 👋\n"
        "Sono il tuo bot per le notizie tech italiane. Scegli una categoria:",
        reply_markup=category_keyboard()
    )


async def send_news(update, category_id):
    category_name = "tutte le categorie" if category_id == "all" else CATEGORIES[category_id]["label"]
    await update.effective_message.reply_text(f"🔍 Cerco le ultime notizie: {category_name}...")
    news_list = []

    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            if category_id != "all" and not matches_category(entry, category_id):
                continue
            title = entry.get("title", "Senza titolo")
            link = entry.get("link", "")
            news_list.append(f"• {title}\n{link}")

    if not news_list:
        await update.effective_message.reply_text(
            f"Non ho trovato notizie per {category_name} al momento.",
            reply_markup=category_keyboard()
        )
        return

    risposta = "\n\n".join(news_list[:15])
    await update.effective_message.reply_text(
        f"📰 Notizie: {category_name}\n\n{risposta}",
        reply_markup=category_keyboard()
    )


async def tech(update, context):
    await send_news(update, "all")


async def tech_button_callback(update, context):
    query = update.callback_query
    await query.answer()
    category_id = query.data.removeprefix("category:")
    if category_id == "all" or category_id in CATEGORIES:
        await send_news(update, category_id)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CallbackQueryHandler(tech_button_callback, pattern=r"^category:"))

    app.run_polling()


if __name__ == "__main__":
    main()
