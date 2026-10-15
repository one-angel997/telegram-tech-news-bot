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
    "https://www.wired.it/feed/tech/",
    "https://www.macitynet.it/feed/",
    "https://www.agendadigitale.eu/feed/",
    "https://www.key4biz.it/feed/",
    "https://www.cybersecurity360.it/feed/"
]

CATEGORIES = {
    "smartphone": {
        "label": "📱 Smartphone e cellulari",
        "keywords": (
            "smartphone", "cellulare", "telefonino", "iphone", "android",
            "samsung", "samsung galaxy", "galaxy s", "galaxy a", "galaxy z",
            "galaxy fold", "galaxy flip", "galaxy note", "xiaomi", "redmi",
            "poco", "google pixel",
            "pixel", "oneplus", "oppo", "vivo", "realme", "motorola", "moto g",
            "huawei", "honor", "nothing phone", "sony xperia", "nokia",
            "asus zenfone", "fairphone", "foldable", "pieghevole",
        ),
    },
    "pc": {
        "label": "💻 PC e laptop",
        "keywords": (
            "laptop", "notebook", "pc", "computer", "processore", "cpu",
            "scheda video", "gpu", "desktop", "macbook", "workstation",
            "scheda madre", "ram", "ssd",
        ),
    },
    "ai": {
        "label": "🤖 AI e affini",
        "keywords": (
            "ai", "ia", "intelligenza artificiale", "machine learning",
            "deep learning", "generative ai", "chatgpt", "openai", "gemini",
            "copilot", "llm", "anthropic", "claude", "mistral", "le chat",
            "meta ai", "llama", "xai", "grok", "deepseek", "perplexity",
            "cohere", "hugging face", "stability ai", "midjourney", "runway ai",
        ),
    },
    "telecom": {
        "label": "📶 Telecomunicazioni",
        "keywords": (
            "telecomunicazioni", "telefonia", "5g", "6g", "fibra ottica",
            "banda larga", "wifi", "wi-fi", "rete mobile", "rete fissa",
            "operatore telefonico", "operatore mobile", "router", "modem",
            "satellite", "satellitare", "comunicazioni satellitari",
            "navigazione satellitare", "galileo", "gnss", "gps", "leonardo",
            "telespazio", "thales alenia space", "starlink", "eutelsat",
            "oneweb", "iris2", "esa", "tim", "vodafone", "windtre", "iliad",
            "fastweb", "open fiber", "fibercop",
        ),
    },
    "informatica": {
        "label": "🖥 Informatica",
        "keywords": (
            "software", "cybersecurity", "sicurezza informatica", "database",
            "cloud", "windows", "linux", "applicazione", "programmazione",
            "linguaggio di programmazione", "internet", "videogioco", ".net",
            "c#", "c++", "python", "java", "javascript", "typescript", "golang",
            "rust", "php", "ruby", "swift", "kotlin", "sql", "powershell",
            "visual basic", "vb.net", "asp.net", "react", "node.js",
        ),
    },
}


def matches_category(entry, category_id):
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".casefold()
    return any(
        re.search(rf"(?<!\w){re.escape(keyword.casefold())}(?![^\W\d_])", text)
        for keyword in CATEGORIES[category_id]["keywords"]
    )


def news_title_key(title):
    return re.sub(r"\W+", " ", title.casefold()).strip()


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
    seen_titles = set()

    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            if category_id != "all" and not matches_category(entry, category_id):
                continue
            title = entry.get("title") or "Senza titolo"
            link = entry.get("link") or ""
            title_key = news_title_key(title) or link
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
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
