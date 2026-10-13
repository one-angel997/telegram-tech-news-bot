import os
import asyncio
import subprocess
import shlex
import re
import feedparser
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Devi impostare TELEGRAM_BOT_TOKEN nel file .env o nell'ambiente")

# Percorso all'eseguibile di llama.cpp (es. $HOME/llama.cpp/main)
LLAMA_CPP_PATH = os.getenv("LLAMA_CPP_PATH", "./main")
# Percorso al modello ggml/gguf quantizzato
MODEL_PATH = os.getenv("MODEL_PATH", "")

# Fonti italiane di news tech
FEEDS = [
    "https://www.hdblog.it/rss/",
    "https://www.smartworld.it/feed",
    "https://rss.hwupgrade.it/news.xml",
    "https://www.tomshw.it/feed/",
    "https://www.everyeye.it/feed/notizie/",
    "https://www.wired.it/feed/tech/"
]

# Default del riassunto in caratteri
DEFAULT_SUMMARY_CHARS = 600

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


def truncate_to_char_limit(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last_p = cut.rfind('.')
    if last_p != -1 and last_p > limit - 200:
        return cut[:last_p+1]
    last_n = cut.rfind('\n')
    if last_n != -1:
        return cut[:last_n]
    return cut


def chunk_text(text: str, max_chunk: int = 1500):
    """Semplice chunker per dividere il testo in blocchi di ~max_chunk caratteri."""
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = start + max_chunk
        # cerca di non troncare a metà frase: cerca l'ultimo punto/space
        if end < length:
            split_at = max(text.rfind('\n', start, end), text.rfind('. ', start, end), text.rfind(' ', start, end))
            if split_at and split_at > start:
                end = split_at + 1
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]


def run_llama_blocking(prompt: str, n_predict: int = 256) -> str:
    """Esegue llama.cpp (o compatibile) in modo sincrono e ritorna l'output come stringa.
    Usa LLAMA_CPP_PATH e MODEL_PATH definiti sopra."""
    if not MODEL_PATH:
        return "[LLM non configurato: imposta la variabile d'ambiente MODEL_PATH con il percorso al modello ggml/gguf]"

    cmd = [LLAMA_CPP_PATH, "-m", MODEL_PATH, "-p", prompt, "--n_predict", str(n_predict), "--temp", "0.2"]
    try:
        # Usiamo subprocess.run in un thread esterno per non bloccare l'event loop
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        out = proc.stdout
        if not out:
            out = proc.stderr
        # some versions echo the prompt back; proviamo a rimuovere l'eco del prompt
        # prendiamo l'ultima parte dell'output come generazione
        lines = out.splitlines()
        if len(lines) > 0:
            # prendi le ultime 1000 chars dall'output
            joined = "\n".join(lines[-40:])
            return joined.strip()
        return out.strip()
    except subprocess.TimeoutExpired:
        return "[Timeout: il modello ha impiegato troppo tempo a rispondere]"
    except FileNotFoundError:
        return f"[Eseguibile LLM non trovato: controlla LLAMA_CPP_PATH (attuale: {LLAMA_CPP_PATH})]"
    except Exception as e:
        return f"[Errore durante l'esecuzione del LLM: {e}]"


async def summarize_text(text: str, target_chars: int = DEFAULT_SUMMARY_CHARS) -> str:
    """Riassume il testo usando un LLM locale con strategia chunk->partial summaries->final summary."""
    if not MODEL_PATH:
        return "Riassunto non disponibile: MODEL_PATH non impostato. Segui le istruzioni nel README per installare un modello locale."

    # Se il testo è già breve, chiediamo un riassunto diretto
    if len(text) <= 1200:
        prompt = f"Sei un assistente che riassume testi in italiano. Riassumi il testo seguente in massimo {target_chars} caratteri, in modo chiaro e coerente, mantenendo solo i punti chiave. Non aggiungere informazioni non presenti.\n\n{text}\n\nRisposta:" 
        # Esegui in thread per non bloccare il loop
        summary = await asyncio.to_thread(run_llama_blocking, prompt, 400)
        return truncate_to_char_limit(summary, target_chars)

    # altrimenti chunkiamo
    chunks = chunk_text(text, max_chunk=1200)
    partials = []
    for ch in chunks:
        prompt = f"Sei un assistente che riassume testi in italiano. Riassumi il testo seguente in massimo 200 caratteri, in 2-4 frasi chiare mantenendo i punti chiave.\n\n{ch}\n\nRisposta:" 
        part = await asyncio.to_thread(run_llama_blocking, prompt, 200)
        partials.append(truncate_to_char_limit(part, 250))

    combined = "\n".join(partials)
    final_prompt = f"Hai ricevuto i seguenti riassunti parziali. Uniscili e crea un riassunto finale in italiano coerente e leggibile. Limita la risposta a massimo {target_chars} caratteri. Mantieni i punti più importanti e rimuovi ripetizioni.\n\n{combined}\n\nRisposta finale:" 
    final = await asyncio.to_thread(run_llama_blocking, final_prompt, 512)
    return truncate_to_char_limit(final, target_chars)

async def tech(update, context, category_id="all"):
    category_name = "tutte le categorie" if category_id == "all" else CATEGORIES[category_id]["label"]
    await update.effective_message.reply_text(f"🔍 Recupero le ultime notizie: {category_name}...")

    news_entries = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            if category_id != "all" and not matches_category(entry, category_id):
                continue

            title = entry.get("title", "Senza titolo")
            link = entry.get("link", "")
            if "content" in entry:
                try:
                    content = entry.content[0].value
                except (AttributeError, IndexError, KeyError, TypeError):
                    content = entry.get("summary", "")
            else:
                content = entry.get("summary", entry.get("description", ""))
            clean = re.sub(r"<[^<]+?>", "", content)
            news_entries.append({"title": title, "link": link, "content": clean})

    if not news_entries:
        await update.effective_message.reply_text(
            f"Non ho trovato notizie per {category_name} al momento.",
            reply_markup=category_keyboard()
        )
        await asyncio.sleep(0.3)
        try:
            await context.application.stop()
        except TypeError:
            context.application.stop()
        return

    entries = news_entries[:10]
    try:
        context.chat_data["last_news"] = entries
    except Exception:
        context.application.bot_data["last_news"] = entries

    msg_lines = []
    keyboard = []
    for index, entry in enumerate(entries):
        msg_lines.append(f"{index + 1}. {entry['title']}\n{entry['link']}")
        keyboard.append([
            InlineKeyboardButton(f"Riassunto {index + 1}", callback_data=f"get_summary:{index}")
        ])
    keyboard.extend(category_keyboard().inline_keyboard)

    risposta = "\n\n".join(msg_lines)
    await update.effective_message.reply_text(
        f"📰 Notizie: {category_name}\n\n{risposta}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Dopo aver inviato le notizie, fermiamo l'applicazione per "auto-distruzione"
    await asyncio.sleep(0.5)  # piccolo ritardo per essere sicuri che i messaggi siano inviati
    try:
        await context.application.stop()
    except TypeError:
        context.application.stop()


async def tech_button_callback(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "get_tech":
        category_id = "all"
    else:
        category_id = query.data.removeprefix("category:")
    if category_id == "all" or category_id in CATEGORIES:
        await tech(update, context, category_id)


async def summary_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data  # formato: get_summary:{i}
    try:
        _, idx = data.split(":")
        idx = int(idx)
    except Exception:
        await query.message.reply_text("Dati del pulsante non validi.")
        return

    # recupera la entry
    entries = context.chat_data.get('last_news') if 'last_news' in context.chat_data else context.application.bot_data.get('last_news')
    if not entries or idx < 0 or idx >= len(entries):
        await query.message.reply_text("Notizia non trovata (sessione scaduta?). Riprova a cercare le notizie.")
        return

    entry = entries[idx]
    await query.message.reply_text(f"📝 Sto creando il riassunto per: {entry['title']}\nAttendi... (quest'operazione può impiegare qualche secondo)")

    # Esegui il riassunto (chiamata all'LLM locale). Non bloccare l'event loop.
    summary = await summarize_text(entry.get('content', '') or entry.get('title', ''), target_chars=DEFAULT_SUMMARY_CHARS)

    # Invia il riassunto come risposta
    text = f"🔖 Riassunto ({DEFAULT_SUMMARY_CHARS} char max):\n\n{summary}\n\nLink: {entry['link']}"
    await query.message.reply_text(text)

    # Dopo aver inviato il riassunto, chiudiamo l'applicazione (comportamento on-demand)
    await asyncio.sleep(0.3)
    try:
        await context.application.stop()
    except TypeError:
        context.application.stop()


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CallbackQueryHandler(tech_button_callback, pattern=r"^(get_tech|category:)") )
    app.add_handler(CallbackQueryHandler(summary_callback, pattern="get_summary:"))

    app.run_polling()


if __name__ == "__main__":
    main()
