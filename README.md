# Telegram News Bot

Bot Telegram in Python che recupera notizie da feed RSS e permette di richiedere un riassunto in italiano. I riassunti sono generati in locale con `llama.cpp` su Android/Termux: `llama-server` carica il modello una volta e il bot invia le richieste al server locale.

A partire dal refactor su `feature/news-bot`, il repository è stato esteso a supportare più profili separati mantenendo una base comune:

- `Tech News` (notizie tecnologiche)
- `F1 News` (notizie di Formula 1 e motorsport)

Tutti i profili condividono la stessa architettura di scraping, filtro, Telegram e riassunto, ma hanno configurazioni, feed e token separati.

## Hardware di riferimento

Configurazione di riferimento: dispositivi Android 13 con 4 GB di RAM con almeno 3 GB di memoria disponibile.

- La RAM, condivisa con Android e le altre app, è il limite principale. La dimensione del file GGUF non corrisponde alla memoria totale richiesta durante l'inferenza.
- Inizia con il modello **Qwen3.5-0.8B Q4_0**. È una scelta leggera per provare il riassunto locale; la qualità in italiano va verificata con le tue notizie.
- Il modello Q4_0 occupa circa 563 MB su disco. Il runtime usa memoria aggiuntiva per contesto e generazione.
- Non iniziare da modelli da 2B o 3B: possono causare rallentamenti o terminare per mancanza di RAM.
- Tieni modello e sorgenti nella memoria privata di Termux (`$HOME`), non sulla microSD.

## Architettura del repository

Il progetto usa una struttura a profili separati ma con codice condiviso:

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
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── feeds/
│   │   ├── __init__.py
│   │   ├── fetcher.py
│   │   └── source_registry.py
│   ├── summarizer/
│   │   ├── __init__.py
│   │   └── llama_client.py
│   └── telegram/
│       ├── __init__.py
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
    └── ...
```

### Principio della struttura

- `app/`: logica condivisa tra tutti i bot
- `bots/<profile>/`: configurazione, feed, keyword e token specifici del profilo
- `bot.py`: entrypoint generico del profilo attivo
- `run_tech_news.py`: wrapper semplice per il profilo Tech News
- `run_f1_news.py`: wrapper semplice per il profilo F1 News

In pratica, il codice di scraping, filtro e riassunto resta unico, mentre i feed e le categorie cambiano a seconda del profilo.

## Funzionalità principali

- Recupero in tempo reale delle notizie tramite feed RSS
- Selezione per categoria tramite pulsanti Telegram
- Supporto a più profili: Tech News e F1 News
- Duplicati rimossi tra feed diversi
- Riassunti in italiano generati in locale con `llama.cpp`
- Comandi `/start`, `/tech` e `/f1`
- Configurazione potenziata per separare token, feed, categorie, e ambiente di runtime

## 1. Preparare Termux

Installa una versione aggiornata di Termux da F-Droid o dalle release ufficiali. Evita versioni obsolete. Apri Termux e aggiorna i pacchetti:

```sh
pkg update && pkg upgrade -y
pkg install -y git cmake clang make python curl
```

Se non hai già una copia del progetto:

```sh
cd "$HOME"
git clone https://github.com/one-angel997/telegram-tech-news-bot.git
cd telegram-tech-news-bot
```

## 2. Compilare llama.cpp e `llama-server`

Lo script incluso scarica i sorgenti ufficiali di `ggml-org/llama.cpp` e compila `llama-server` con un solo job, per contenere il picco di memoria durante la build:

```sh
cd "$HOME/telegram-tech-news-bot"
sh termux/install_llama.sh
```

La compilazione può richiedere tempo e spazio temporaneo. Il percorso atteso a fine build è:

```text
$HOME/llama.cpp/build/bin/llama-server
```

Se la compilazione viene terminata da Android, chiudi le app non necessarie, lascia Termux in primo piano e riprova. Non copiare un eseguibile compilato per PC: deve essere compilato per Android/ARM64.

## 3. Scaricare il modello GGUF

Scarica la quantizzazione Q4_0 pubblicata nel repository GGUF del progetto `ggml-org`:

```sh
mkdir -p "$HOME/models"
curl -L --fail --retry 3 \
  "https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q4_0.gguf" \
  -o "$HOME/models/Qwen3.5-0.8B-Q4_0.gguf"
ls -lh "$HOME/models/Qwen3.5-0.8B-Q4_0.gguf"
```

Il file è di circa 563 MB. Il repository del modello indica licenza Apache-2.0; controlla sempre la scheda del modello e i termini correnti prima dell'uso.

## 4. Avviare il server locale

Apri una sessione Termux e avvia il server in primo piano:

```sh
cd "$HOME/telegram-tech-news-bot"
sh termux/start_llama_server.sh
```

Il server carica il modello e ascolta solo su `127.0.0.1:8080`, quindi non è esposto alla rete locale. Al primo avvio attendi che il caricamento sia completato. In una seconda sessione Termux puoi controllare che risponda:

```sh
curl http://127.0.0.1:8080/health
```

## 5. Installare e configurare il bot

In una seconda sessione Termux:

```sh
cd "$HOME/telegram-tech-news-bot"
pkg install -y python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crea i bot con [@BotFather](https://t.me/BotFather), quindi crea i file di ambiente per i profili:

```sh
# Tech News
cat > bots/tech_news/.env <<'EOF'
TELEGRAM_BOT_TOKEN=INSERISCI_IL_TOKEN_TECH
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_REQUEST_TIMEOUT=180
BOT_PROFILE=tech_news
EOF

# F1 News
cat > bots/f1_news/.env <<'EOF'
TELEGRAM_BOT_TOKEN=INSERISCI_IL_TOKEN_F1
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_REQUEST_TIMEOUT=180
BOT_PROFILE=f1_news
EOF
```

Il file `.env` è sempre personale e non va condiviso nel repository. In `bots/<profile>/.env` va inserito solo il token di quel bot e i parametri locali del profilo.

## 6. Configurazione del profilo

Ogni profilo ha un file `config.yaml` separato.

### Tech News

File: `bots/tech_news/config.yaml`

```yaml
bot:
  display_name: "Tech News Bot"
  token: "${TELEGRAM_BOT_TOKEN}"

feeds:
  - https://www.hdblog.it/rss/
  - https://www.smartworld.it/feed
  - https://rss.hwupgrade.it/news.xml
  - https://www.tomshw.it/feed/
  - https://www.everyeye.it/feed/notizie/
  - https://www.wired.it/feed/tech/
  - https://www.macitynet.it/feed/
  - https://www.agendadigitale.eu/feed/
  - https://www.key4biz.it/feed/
  - https://www.cybersecurity360.it/feed/

categories:
  smartphone:
    label: "📱 Smartphone e cellulari"
    keywords:
      - smartphone
      - iphone
      - android
      - samsung
      - xiaomi
      - google pixel
  pc:
    label: "💻 PC e laptop"
    keywords:
      - laptop
      - pc
      - processore
      - gpu
      - scheda video
  ai:
    label: "🤖 AI"
    keywords:
      - ai
      - ia
      - chatgpt
      - openai
      - gemini
  telecom:
    label: "📶 Telecomunicazioni"
    keywords:
      - 5g
      - wifi
      - fibra ottica
      - tim
      - vodafone
  informatica:
    label: "🖥 Informatica"
    keywords:
      - software
      - cybersecurity
      - linux
      - python
      - cloud

llama:
  server_url: "http://127.0.0.1:8080"
  request_timeout: 180
```

### F1 News

File: `bots/f1_news/config.yaml`

```yaml
bot:
  display_name: "F1 News Bot"
  token: "${TELEGRAM_BOT_TOKEN}"

feeds:
  - https://www.racefans.net/feed/
  - https://www.formula1.com/content/fom-website/en/latest-headlines.rss
  - https://www.autosport.com/rss/f1/
  - https://www.gpblog.com/en/rss.xml
  - https://motorsport.uol.com.br/rss/f1/

categories:
  weekend:
    label: "🏁 Weekend GP"
    keywords:
      - gran premio
      - gp
      - gara
      - qualifiche
      - sprint
  teams:
    label: "🏎️ Team e piloti"
    keywords:
      - ferrari
      - red bull
      - mercedes
      - mclaren
      - verstappen
      - leclerc
      - piastri
      - hamilton
  tech:
    label: "⚙️ Tecnologia"
    keywords:
      - aerodinamica
      - telaio
      - motore
      - power unit
      - sospensioni
  news:
    label: "📰 Generale"
    keywords:
      - f1
      - formula 1
      - paddock
      - pit lane

llama:
  server_url: "http://127.0.0.1:8080"
  request_timeout: 180
```

## 7. Avvio dei bot

Per il bot Tech News:

```sh
source .venv/bin/activate
BOT_PROFILE=tech_news python bot.py
# oppure
python run_tech_news.py
```

Per il bot F1 News:

```sh
source .venv/bin/activate
BOT_PROFILE=f1_news python bot.py
# oppure
python run_f1_news.py
```

## 8. Come funziona il riassunto

Quando premi il pulsante per un riassunto, il bot invia una richiesta all'API compatibile OpenAI di `llama-server` su `127.0.0.1`. Il modello resta caricato tra una richiesta e l'altra, invece di essere riaperto a ogni generazione.

Il testo inviato al modello è limitato ai primi 6000 caratteri e il riassunto restituito è limitato a 600 caratteri. Se il server non è raggiungibile, il bot registra l'errore e lo segnala in chat.

## 9. Struttura logica della base comune

La base comune del progetto è organizzata così:

- `app/common/config.py`: carica il profilo attivo e i file `.env` + `config.yaml`
- `app/feeds/source_registry.py`: espone feed e categorie del profilo
- `app/feeds/fetcher.py`: recupera e parse RSS
- `app/summarizer/llama_client.py`: invoca `llama-server` per riassunti in italiano
- `app/telegram/handlers.py`: logica di Telegram, fetch dei feed, selezione delle categorie e callback dei riassunti
- `app/telegram/keyboards.py`: pulsanti inline per Telegram
- `app/telegram/bot.py`: bootstrap dell'ApplicationBuilder

Questa separazione consente di usare lo stesso codice per più bot senza duplicare la comunicazione Telegram, il filtro dei feed o il riassunto LLM.

## 10. Risoluzione dei problemi

- `llama-server non trovato`: esegui `sh termux/install_llama.sh` e verifica il percorso `$HOME/llama.cpp/build/bin/llama-server`.
- `Modello GGUF non trovato`: controlla che il download sia completato e che il file si trovi in `$HOME/models/`.
- `Errore di connessione dal bot`: avvia prima `llama-server` e verifica `/health` da un'altra sessione.
- `Processo terminato o telefono molto lento`: chiudi le app non necessarie, riduci `LLAMA_CONTEXT_SIZE` e usa il modello 0.8B.
- `Qualità del riassunto insufficiente`: controlla il testo fornito dal feed RSS.
- `Token mancante`: verifica che il file `.env` nel profilo scelto esista e sia corretto.
- `File di configurazione non trovato`: verifica che `bots/<profile>/config.yaml` sia presente.

## 11. Dipendenze e risorse

- Dipendenze Python: `python-telegram-bot`, `feedparser`, `python-dotenv`, `PyYAML`, `requests`
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Modello Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)
- [File GGUF Q4_0](https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF)

## 12. Esempio di workflow operativo

1. Avvia `llama-server`
2. Avvia il bot Tech News con la config `tech_news`
3. Testa `/start` e scegli una categoria
4. Verifica che i feed vengano caricati
5. Clicca un pulsante di riassunto
6. Controlla la qualità del riassunto
7. Ripeti i test con il bot F1 usando il profilo `f1_news`

Questo è il workflow corretto per mantenere lo stesso codice base, ma con due identità Telegram distinte e configurazioni totalmente indipendenti.
