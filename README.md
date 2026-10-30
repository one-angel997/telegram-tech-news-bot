# Telegram Tech News Bot

Bot Telegram in Python che recupera notizie tech da feed RSS italiani e permette di
richiedere un riassunto in italiano. I riassunti sono generati in locale con
`llama.cpp` su Android/Termux: `llama-server` carica il modello una volta e il bot
invia le richieste al server locale.

## Hardware di riferimento

Configurazione di riferimento: dispositivi Android 13 con 4 GB di RAM con almeno 3 GB di memoria disponibile.

- La RAM, condivisa con Android e le altre app, è il limite principale. La dimensione
  del file GGUF non corrisponde alla memoria totale richiesta durante l'inferenza.
- Inizia con il modello **Qwen3.5-0.8B Q4_0**. È una scelta leggera per provare il
  riassunto locale; la qualità in italiano va verificata con le tue notizie.
- Il modello Q4_0 occupa circa 563 MB su disco. Il runtime usa memoria aggiuntiva
  per contesto e generazione.
- Non iniziare da modelli da 2B o 3B: possono causare rallentamenti o terminare per
  mancanza di RAM. Valuta un 2B solo dopo aver misurato l'uso reale; non è garantito
  che Android lo mantenga in memoria.
- Tieni modello e sorgenti nella memoria privata di Termux (`$HOME`), non sulla microSD.

## Funzionalità principali

- Recupero in tempo reale delle notizie tech italiane tramite feed RSS
- Selezione per smartphone e cellulari, PC e laptop, AI, telecomunicazioni e informatica, con filtri per marchi, modelli e tecnologie
- Rimozione dei titoli duplicati trovati su più feed RSS
- Invio di ogni notizia in un messaggio separato, con il relativo pulsante per il riassunto
- Riassunti in italiano generati in locale con `llama.cpp`
- Comandi `/start` e `/tech` e selezione delle categorie tramite pulsanti Telegram

## 1. Preparare Termux

Installa una versione aggiornata di Termux da F-Droid o dalle release ufficiali
Termux su GitHub; evita versioni obsolete. Apri Termux e aggiorna i pacchetti:

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

Lo script incluso scarica i sorgenti ufficiali di `ggml-org/llama.cpp` e compila
`llama-server` con un solo job, per contenere il picco di memoria durante la build:

```sh
cd "$HOME/telegram-tech-news-bot"
sh termux/install_llama.sh
```

La compilazione può richiedere tempo e spazio temporaneo. Il percorso atteso a fine
build è:

```text
$HOME/llama.cpp/build/bin/llama-server
```

Se la compilazione viene terminata da Android, chiudi le app non necessarie, lascia
Termux in primo piano e riprova. Non copiare un eseguibile compilato per PC: deve
essere compilato per Android/ARM64.

## 3. Scaricare il modello GGUF

Scarica la quantizzazione Q4_0 pubblicata nel repository GGUF del progetto `ggml-org`:

```sh
mkdir -p "$HOME/models"
curl -L --fail --retry 3 \
  "https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q4_0.gguf" \
  -o "$HOME/models/Qwen3.5-0.8B-Q4_0.gguf"
ls -lh "$HOME/models/Qwen3.5-0.8B-Q4_0.gguf"
```

Il file è di circa 563 MB. Il repository del modello indica licenza Apache-2.0;
controlla sempre la scheda del modello e i termini correnti prima dell'uso.
Il modello base Qwen3.5-0.8B è multilingue, ma un modello piccolo può sbagliare o
perdere dettagli: verifica i riassunti rispetto agli articoli originali.

## 4. Avviare il server locale

Apri una sessione Termux e avvia il server in primo piano:

```sh
cd "$HOME/telegram-tech-news-bot"
sh termux/start_llama_server.sh
```

Il server carica il modello e ascolta solo su `127.0.0.1:8080`, quindi non è esposto
alla rete locale. Al primo avvio attendi che il caricamento sia completato. In una
seconda sessione Termux puoi controllare che risponda:

```sh
curl http://127.0.0.1:8080/health
```

Il server usa un contesto di 4096 token e 4 thread per impostazione predefinita.
Puoi personalizzare le risorse prima dell'avvio:

```sh
LLAMA_CONTEXT_SIZE=2048 LLAMA_THREADS=2 sh termux/start_llama_server.sh
```

Ridurre il contesto può aiutare se Android chiude il processo per mancanza di
memoria, a costo di ridurre il testo disponibile al modello. Mantieni aperta la
sessione del server mentre usi il bot. Per evitare sospensioni durante le prove,
puoi eseguire `termux-wake-lock` e consentire a Termux di funzionare in background
nelle impostazioni di batteria di Android. Non è consigliato creare swap con un
file su `/sdcard`: i permessi Android/Termux in genere non consentono di attivarlo
come memoria virtuale.

## 5. Installare e configurare il bot

In una seconda sessione Termux:

```sh
cd "$HOME/telegram-tech-news-bot"
pkg install -y python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crea il bot con [@BotFather](https://t.me/BotFather), quindi crea il file `.env`
nella cartella del progetto:

```sh
cat > .env <<'EOF'
TELEGRAM_BOT_TOKEN=INSERISCI_IL_TOKEN
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_REQUEST_TIMEOUT=180
EOF
chmod 600 .env
```

Non condividere il token e non inserirlo nel repository. `.env` è escluso da Git.
`LLAMA_SERVER_URL` e `LLAMA_REQUEST_TIMEOUT` sono opzionali se i valori predefiniti
vanno bene.

Avvia il bot lasciando il server attivo nell'altra sessione:

```sh
source .venv/bin/activate
python bot.py
```

Per usarlo da Termux:Widget, copia `termux/start_tech_news_bot.sh` in
`~/.shortcuts/` e rendilo eseguibile. Avvia prima `llama-server` e poi il bot:

```sh
mkdir -p "$HOME/.shortcuts"
cp termux/start_tech_news_bot.sh "$HOME/.shortcuts/"
chmod +x "$HOME/.shortcuts/start_tech_news_bot.sh"
```

## Come funziona il riassunto

Quando premi il pulsante per un riassunto, il bot invia una singola richiesta
all'API compatibile OpenAI di `llama-server` su `127.0.0.1`. Il modello resta
caricato tra una richiesta e l'altra, invece di essere riaperto a ogni generazione.
Il testo inviato al modello è limitato ai primi 6000 caratteri e il riassunto
restituito è limitato a 600 caratteri. Se il server non è raggiungibile, il bot
registra l'errore e lo segnala in chat.

## Risoluzione dei problemi

- **`llama-server non trovato`**: esegui `sh termux/install_llama.sh`; verifica il
  percorso `$HOME/llama.cpp/build/bin/llama-server`.
- **`Modello GGUF non trovato`**: controlla che il download sia terminato e che il
  file si trovi in `$HOME/models/`.
- **Errore di connessione dal bot**: avvia prima `termux/start_llama_server.sh` e
  verifica `/health` da un'altra sessione.
- **Processo terminato o telefono molto lento**: chiudi le app non necessarie,
  riduci `LLAMA_CONTEXT_SIZE` (ad esempio a 2048) e usa il modello 0.8B. Evita di
  lasciare contemporaneamente altri modelli o applicazioni pesanti in memoria.
- **Qualità del riassunto insufficiente**: controlla il testo fornito dal feed RSS.
  Il bot riassume solo il contenuto presente nel feed; non apre automaticamente la
  pagina web dell'articolo.

## Dipendenze e risorse

- Dipendenze Python: `python-telegram-bot`, `feedparser`, `python-dotenv`.
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Modello Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)
- [File GGUF Q4_0](https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF)
