#!/data/data/com.termux/files/usr/bin/sh

set -e

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-rss-check"

if [ ! -d "$VENV_DIR" ]; then
  python -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --quiet requests beautifulsoup4 feedparser

"$VENV_DIR/bin/python" - <<'PY'
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

sites = {
    "Androidworld": "https://androidworld.it",
    "Dday.it": "https://www.dday.it",
    "AI News": "https://ainews.it",
    "Rivista.AI": "https://rivista.ai",
    "AI4Business": "https://www.ai4business.it",
    "CorCom": "https://www.corrierecomunicazioni.it",
    "Punto Informatico": "https://www.punto-informatico.it",
    "ICT Security Magazine": "https://www.ictsecuritymagazine.com",
}

headers = {"User-Agent": "Mozilla/5.0 (compatible; Telegram-News-Bot-RSS-Check/1.0)"}

print("Verifica feed RSS/Atom")
print("=" * 70)

for name, homepage in sites.items():
    print(f"\n{name}: {homepage}")

    try:
        response = requests.get(homepage, timeout=20, headers=headers, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for tag in soup.find_all("link", href=True):
            feed_type = tag.get("type", "").lower()
            rel = " ".join(tag.get("rel", [])).lower()
            href = tag["href"]

            if "rss+xml" in feed_type or "atom+xml" in feed_type or "alternate" in rel:
                if "feed" in href.lower() or "rss" in href.lower() or "atom" in href.lower():
                    links.append(urljoin(response.url, href))

        if not links:
            print("  Nessun feed RSS/Atom dichiarato nella homepage.")
            print("  Da controllare manualmente nel footer o nel codice sorgente.")
            continue

        for feed_url in dict.fromkeys(links):
            feed = feedparser.parse(feed_url)
            entries_count = len(feed.entries)
            status = getattr(feed, "status", None)
            format_name = feed.version or "non riconosciuto"

            print(f"  Feed: {feed_url}")
            print(f"    HTTP: {status or 'sconosciuto'}, formato: {format_name}, voci: {entries_count}")

            if entries_count:
                latest = feed.entries[0]
                print(f"    Ultima voce: {latest.get('title', '(senza titolo)')}")
                print(f"    Link: {latest.get('link', '(nessun link)')}")
            else:
                print("    Nessuna voce disponibile.")

    except requests.RequestException as error:
        print(f"  Impossibile raggiungere il sito: {error}")
    except Exception as error:
        print(f"  Verifica fallita: {error}")
PY
