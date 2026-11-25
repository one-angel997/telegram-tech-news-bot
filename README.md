# Telegram News Bot

Bot Telegram in Python che recupera notizie da feed RSS e permette di richiedere un riassunto in italiano. I riassunti sono generati in locale con `llama.cpp` su Android/Termux: `llama-server` carica il modello una volta e il bot invia le richieste al server locale.

Il repository supporta più profili separati mantenendo una base comune:

- `Tech News`: notizie tecnologiche italiane
- `F1 News`: notizie di Formula 1 e motorsport

Tutti i profili condividono la stessa architettura per scraping, filtro, Telegram e riassunto. Feed, categorie e token restano separati.

## Funzionalità principali

- Recupero in tempo reale delle notizie tramite feed RSS
- Selezione delle categorie tramite pulsanti Telegram
- Invio di ogni notizia in un messaggio separato, con pulsante di riassunto dedicato
- Pausa di un secondo tra un messaggio e l'altro
- Rimozione dei titoli duplicati trovati su più feed RSS
- Tastiera delle categorie riproposta al termine dell'elenco
- Riassunti in italiano generati in locale con `llama.cpp`
- Supporto a più bot separati con profili e token indipendenti
- Comandi `/start`, `/tech` e `/f1`

## Architettura del repository

```text
telegram-tech-news-bot/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── bot.py
├── run_tech_news.py
├── run_f1_news.py
├── app/
│   ├── common/
│   │   ├── config.py
│   │   └── logging.py
│   ├── feeds/
│   │   ├── fetcher.py
│   │   └── source_registry.py
│   ├── summarizer/
│   │   └── llama_client.py
│   └── telegram/
│       ├── bot.py
│       ├── handlers.py
│       └── keyboards.py
├── bots/
│   ├── tech_news/
│   │   ├── .env
│   │   └── config.yaml
│   └── f1_news/
│       ├── .env
│       └── config.yaml
└── termux/
```

### Responsabilità dei principali moduli

- `app/common/config.py`: determina il profilo attivo e carica `.env` e `config.yaml`
- `app/feeds/source_registry.py`: espone feed RSS e categorie del profilo
- `app/feeds/fetcher.py`: recupera e analizza i feed RSS
- `app/summarizer/llama_client.py`: genera i riassunti tramite `llama-server`
- `app/telegram/handlers.py`: gestisce comandi, recupero notizie, messaggi separati e riassunti
- `app/telegram/keyboards.py`: crea le tastiere delle categorie e dei riassunti
- `app/telegram/bot.py`: costruisce l'applicazione Telegram e registra gli handler
- `bot.py`: entrypoint generico selezionabile tramite `BOT_PROFILE`
- `run_tech_news.py`: avvio dedicato al profilo Tech News
- `run_f1_news.py`: avvio dedicato al profilo F1 News

## Hardware di riferimento

Configurazione di riferimento: dispositivi Android 13 con 4 GB di RAM e almeno 3 GB di memoria disponibile.

- La RAM è condivisa con Android e le altre app ed è il limite principale
- Il modello consigliato è **Qwen3.5-0.8B Q4_0**
- Il file Q4_0 occupa circa 563 MB su disco
- Il runtime richiede memoria aggiuntiva per contesto e generazione
- Modelli da 2B o 3B possono essere terminati da Android per mancanza di RAM
- Tieni modello e sorgenti nella memoria privata di Termux (`$HOME`), non sulla microSD

## 1. Preparare Termux

Installa una versione aggiornata di Termux da F-Droid o dalle release ufficiali. Apri Termux e aggiorna i pacchetti:

```sh
pkg update && pkg upgrade -y
pkg install -y git cmake clang make python curl
```

Clona il repository:

```sh
cd "$HOME"
git clone https://github.com/one-angel997/telegram-tech-news-bot.git
cd telegram-tech-news-bot
```

## 2. Compilare llama.cpp e `llama-server`

```sh
sh termux/install_llama.sh
```

Il percorso atteso a fine build è:

```text
$HOME/llama.cpp/build/bin/llama-server
```

## 3. Scaricare il modello GGUF

```sh
mkdir -p "$HOME/models"
curl -L --fail --retry 3 \
  "https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q4_0.gguf" \
  -o "$HOME/models/Qwen3.5-0.8B-Q4_0.gguf"
ls -lh "$HOME/models/Qwen3.5-0.8B-Q4_0.gguf"
```

Il file è di circa 563 MB e usa licenza Apache-2.0. Verifica sempre i termini del modello prima dell'uso.

## 4. Avviare il server locale

```sh
sh termux/start_llama_server.sh
```

Il server resta disponibile su `127.0.0.1:8080`. Da una seconda sessione Termux puoi verificarlo:

```sh
curl http://127.0.0.1:8080/health
```

## 5. Installare le dipendenze Python

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 6. Configurare i profili Telegram

Crea i due bot con [@BotFather](https://t.me/BotFather). Ogni bot usa un file `.env` separato:

```sh
cat > bots/tech_news/.env <<'EOF'
TELEGRAM_BOT_TOKEN=INSERISCI_IL_TOKEN_TECH
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_REQUEST_TIMEOUT=180
BOT_PROFILE=tech_news
EOF

cat > bots/f1_news/.env <<'EOF'
TELEGRAM_BOT_TOKEN=INSERISCI_IL_TOKEN_F1
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_REQUEST_TIMEOUT=180
BOT_PROFILE=f1_news
EOF

chmod 600 bots/tech_news/.env bots/f1_news/.env
```

I token Telegram non devono essere inseriti nel repository. Entrambi i file `.env` specifici dei profili sono esclusi da Git.

## 7. Configurazione di feed e categorie

Ogni profilo contiene un file `bots/<profile>/config.yaml` con:

- nome visualizzato del bot
- token Telegram risolto dall'ambiente
- feed RSS
- categorie
- keyword
- parametri di `llama-server`

Il profilo Tech usa `bots/tech_news/config.yaml`. Il profilo F1 usa `bots/f1_news/config.yaml`.

## 8. Avviare i bot

Avvia il bot Tech News:

```sh
python run_tech_news.py
```

Oppure avvia lo stesso entrypoint generico con il profilo Tech:

```sh
BOT_PROFILE=tech_news python bot.py
```

Avvia il bot F1 News:

```sh
python run_f1_news.py
```

Oppure:

```sh
BOT_PROFILE=f1_news python bot.py
```

## 9. Modalità di ricezione delle notizie

Quando viene richiesta una categoria:

1. il bot recupera al massimo cinque elementi per ciascun feed
2. elimina i titoli duplicati
3. limita il risultato a dieci notizie
4. invia una singola notizia per messaggio Telegram
5. associa a ogni messaggio il pulsante `Riassunto N`
6. attende un secondo tra un messaggio e il successivo
7. mostra infine una tastiera per scegliere un'altra categoria

Le notizie vengono mantenute in `context.chat_data["last_news"]` finché resta attiva la chat. Il callback del riassunto usa l'indice nel pulsante per recuperare il contenuto corretto.

## 10. Come funziona il riassunto

Premendo un pulsante `Riassunto N`, il bot invia una richiesta all'API compatibile OpenAI di `llama-server` su `127.0.0.1`.

Il testo inviato al modello è limitato ai primi 6000 caratteri. Il riassunto restituito viene limitato a 600 caratteri e viene inviato insieme al link della notizia.

Se il server non è raggiungibile, il bot registra l'errore e lo segnala in chat.

## 11. Risoluzione dei problemi

- `llama-server non trovato`: esegui `sh termux/install_llama.sh` e verifica il percorso `$HOME/llama.cpp/build/bin/llama-server`
- `Modello GGUF non trovato`: controlla che il download sia terminato e che il file si trovi in `$HOME/models/`
- `Errore di connessione dal bot`: avvia `llama-server` e verifica `/health` da un'altra sessione
- `Token mancante`: controlla il file `.env` del profilo selezionato
- `File di configurazione non trovato`: verifica che `bots/<profile>/config.yaml` esista
- `Processo terminato o telefono molto lento`: chiudi app inutili, riduci `LLAMA_CONTEXT_SIZE` e usa il modello 0.8B
- `Qualità del riassunto insufficiente`: controlla il testo presente nel feed RSS

## 12. Dipendenze e risorse

- Dipendenze Python: `python-telegram-bot`, `feedparser`, `python-dotenv`, `PyYAML`, `requests`
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Modello Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)
- [File GGUF Q4_0](https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF)
