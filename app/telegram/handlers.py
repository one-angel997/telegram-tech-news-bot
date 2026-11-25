import asyncio
import re

from telegram import Update

from app.common.config import get_config
from app.common.logging import logger
from app.feeds.fetcher import fetch_feed
from app.feeds.source_registry import get_categories, get_feed_urls
from app.summarizer.llama_client import summarize_text
from app.telegram.keyboards import build_category_keyboard, build_summary_keyboard


NEWS_SEND_DELAY_SECONDS = 1
MAX_NEWS_PER_REQUEST = 10
MAX_ENTRIES_PER_FEED = 5


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", title.casefold()).strip()


def clean_summary(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def matches_category(entry, category_id: str, categories: dict) -> bool:
    if category_id == "all":
        return True

    category = categories.get(category_id, {})
    keywords = category.get("keywords", [])
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".casefold()

    return any(
        re.search(rf"(?<!\w){re.escape(keyword.casefold())}(?!\w)", text)
        for keyword in keywords
    )


async def start(update: Update, context):
    config = get_config()
    categories = get_categories()
    bot_name = config.get("bot", {}).get("display_name", "News Bot")

    await update.message.reply_text(
        f"Ciao! 👋\nSono il bot {bot_name}.\nScegli una categoria:",
        reply_markup=build_category_keyboard(categories),
    )


async def fetch_news(category_id: str = "all"):
    entries = []
    seen = set()
    categories = get_categories()

    for feed_url in get_feed_urls():
        feed = fetch_feed(feed_url)
        for item in feed.entries[:MAX_ENTRIES_PER_FEED]:
            if category_id != "all" and not matches_category(item, category_id, categories):
                continue

            title = item.get("title") or "Senza titolo"
            link = item.get("link") or ""

            key = normalize_title(title) or link
            if key in seen:
                continue
            seen.add(key)

            content = item.get("summary") or item.get("description") or ""
            if "content" in item:
                try:
                    content = item.content[0].value
                except (AttributeError, IndexError, KeyError, TypeError):
                    pass

            entries.append({
                "title": title,
                "link": link,
                "content": clean_summary(content),
            })

    return entries[:MAX_NEWS_PER_REQUEST]


async def list_news(update: Update, context, category_id: str = "all"):
    categories = get_categories()
    category_name = (
        "tutte le categorie"
        if category_id == "all"
        else categories.get(category_id, {}).get("label", category_id)
    )

    await update.effective_message.reply_text(
        f"🔍 Recupero le ultime notizie: {category_name}..."
    )

    entries = await fetch_news(category_id)
    if not entries:
        await update.effective_message.reply_text(
            f"Non ho trovato notizie per {category_name} al momento.",
            reply_markup=build_category_keyboard(categories),
        )
        return

    context.chat_data["last_news"] = entries

    # Invia una notizia per messaggio, ciascuna con il proprio pulsante riassunto.
    # La pausa riduce il rischio di superare i limiti di invio di Telegram.
    for index, entry in enumerate(entries):
        if index:
            await asyncio.sleep(NEWS_SEND_DELAY_SECONDS)

        text = f"📰 {index + 1}. {entry['title']}"
        if entry["link"]:
            text += f"\n{entry['link']}"

        await update.effective_message.reply_text(
            text,
            reply_markup=build_summary_keyboard(index),
        )

    await asyncio.sleep(NEWS_SEND_DELAY_SECONDS)
    await update.effective_message.reply_text(
        "Scegli un'altra categoria per continuare:",
        reply_markup=build_category_keyboard(categories),
    )


async def summary_callback(update: Update, context):
    query = update.callback_query
    await query.answer()

    data = query.data
    try:
        _, idx = data.split(":")
        idx = int(idx)
    except (ValueError, TypeError):
        await query.message.reply_text("Dati non validi.")
        return

    entries = context.chat_data.get("last_news", [])
    if idx < 0 or idx >= len(entries):
        await query.message.reply_text("Notizia non trovata. Riprova a richiedere le notizie.")
        return

    entry = entries[idx]
    await query.message.reply_text(
        f"📝 Sto preparando il riassunto di:\n{entry['title']}\nAttendi..."
    )

    try:
        summary = summarize_text(entry.get("content") or entry.get("title"), target_chars=600)
        await query.message.reply_text(
            f"🔖 Riassunto:\n\n{summary}\n\nLink: {entry['link']}"
        )
    except RuntimeError as exc:
        logger.exception("Errore nel riassunto")
        await query.message.reply_text(f"Non sono riuscito a generare il riassunto: {exc}")
