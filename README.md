# 📡 Telegram Tech News Bot

Un bot Telegram scritto in **Python**, pensato per girare anche in **Termux** su Android, che recupera le ultime notizie tecnologiche da fonti italiane come **HDblog, SmartWorld, Hardware Upgrade, Tom's HW, Everyeye, Wired**.

---

## 🚀 Funzionalità

- Recupero in tempo reale delle notizie tech italiane tramite feed RSS
- Comando `/start` per presentazione del bot
- Comando `/tech` per ottenere le ultime novità
- Codice semplice, estendibile e adatto a essere eseguito in Termux

---

## 🛠️ Tecnologie utilizzate

- **Python 3**
- **[python-telegram-bot](https://python-telegram-bot.org/)**
- **[feedparser](https://pypi.org/project/feedparser/)**
- **python-dotenv** (per caricare il token da un file `.env`)
- **Termux** (opzionale, per esecuzione su Android)

---

## 📲 Creazione del bot su Telegram

1. Apri Telegram.
2. Cerca **@BotFather**.
3. Esegui il comando:

   ```text
   /newbot
   ```
4. Scegli un nome per il bot (es. Tech News Bot) e un username che termini con `bot` (es. `tech_news_bot`).
5. BotFather ti fornirà un TOKEN simile a:

   ```text
   1234567890:ABCdefGHIjkLMNopQRstuVWxyz
   ```

---

## 🔐 Configurazione del token (consigliato: file .env)

Per motivi di sicurezza è preferibile non inserire il token direttamente nel codice. Questo repository ora usa `python-dotenv` per leggere la variabile `TELEGRAM_BOT_TOKEN` da un file `.env` nella cartella del progetto.

1. Installa la dipendenza (virtualenv consigliato):

   ```bash
   pip install python-dotenv
   ```

2. Crea un file `.env` nella cartella del progetto con questo contenuto (sostituisci il placeholder con il token reale):

   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjkLMNopQRstuVWxyz
   ```

   Nota: non aggiungere virgolette attorno al token e non aggiungere spazi extra o newline alla fine della riga.

3. `.env` è già incluso in `.gitignore` per evitare di commettere il token accidentalmente.

---

## ⚙️ Esecuzione in Termux (Android)

Esempio rapido di comandi da eseguire in Termux nella cartella del progetto:

```bash
# (opzionale) crea e attiva virtualenv
python -m venv venv
source venv/bin/activate

# installa dipendenze
pip install -r requirements.txt
# oppure
pip install python-dotenv python-telegram-bot feedparser

# crea .env (aprilo con un editor e incolla il token)
echo "TELEGRAM_BOT_TOKEN=INSERISCI_IL_TUO_TOKEN_TELEGRAM" > .env
chmod 600 .env

# avvia il bot
python bot.py
```

Se preferisci non usare `python-dotenv`, puoi esportare la variabile nella shell prima di eseguire il bot:

```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjkLMNopQRstuVWxyz"
python bot.py
```

---

## ℹ️ Note finali

- Non condividere il token pubblicamente.
- Controlla `bot.py` per altre opzioni o personalizzazioni delle fonti RSS.

Buon lavoro! Se vuoi, posso aggiungere un `requirements.txt` con le dipendenze consigliate.