# Telegram News Bot

Bot Telegram scritto in Python che recupera notizie da feed RSS e genera riassunti con `llama.cpp`.

Questo repository usa una base condivisa per più bot, con profili separati:
- Tech News
- F1 News

## Struttura

- `app/` contiene la logica condivisa
- `bots/<profile>/` contiene `.env` e `config.yaml` per ogni bot
- `run_tech_news.py` avvia il bot Tech News
- `run_f1_news.py` avvia il bot F1 News

## Installazione

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Avvio

```bash
python run_tech_news.py
# oppure
python run_f1_news.py
```

## Configurazione

I bot usano un file `.env` separato per profilo:

```bash
bots/tech_news/.env
bots/f1_news/.env
```

contenenti:

```dotenv
TELEGRAM_BOT_TOKEN=...
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_REQUEST_TIMEOUT=180
BOT_PROFILE=tech_news
```

## Configurazione di feed e categorie

Ogni profilo ha un file `config.yaml` per:
- feed RSS
- categorie
- keywords
- parametri del riassunto

## Nota

I token Telegram non vanno mai salvati nel repository. Usa sempre `.env` locale per profilo.
