# 📡 Telegram Tech News Bot

Un bot Telegram scritto in **Python**, pensato per girare anche in **Termux** su Android, che recupera le ultime notizie tecnologiche da fonti italiane come **HDblog, SmartWorld, Hardware Upgrade, Tom's HW, Everyeye e Wired**.

---

## 🚀 Funzionalità

- Recupero in tempo reale delle notizie tech italiane tramite feed RSS
- Comando `/start` per presentazione del bot
- Comando `/tech` per ottenere le ultime novità
- Pulsante inline per recuperare le notizie con un tap
- Auto-terminazione: il bot si chiude automaticamente dopo aver inviato le notizie (utile per eseguirlo on-demand da Termux)

---

## 🛠️ Tecnologie utilizzate

- **Python 3**
- **[python-telegram-bot](https://python-telegram-bot.org/)**
- **[feedparser](https://pypi.org/project/feedparser/)**
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
   `1234567890:ABCdefGHIjkLMNopQRstuVWxyz`

6. Inserisci il token nel file `bot.py` (sostituendo il valore di `TOKEN`) oppure esportalo come variabile d'ambiente in Termux:

```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjkLMNopQRstuVWxyz"
```

---

## ▶️ Eseguire il bot in Termux (on-demand con Termux:Widget)

La soluzione più semplice per avviare il bot solo quando ti serve è usare Termux insieme all'add-on Termux:Widget. Il bot è stato aggiornato per auto-terminarsi dopo aver inviato le notizie, quindi puoi:

- Avviare il bot con un singolo tap sulla schermata principale (widget).
- Aprire Telegram e premere il pulsante inline; il bot riceverà l'update, invierà le notizie e poi si chiuderà automaticamente.

Passaggi rapidi:

1. Installa Termux (consigliato da F-Droid) e avvialo.
2. Installa Termux:Widget dall'app store (F-Droid / Play Store) e concedi i permessi richiesti.
3. Clona questo repository o copia `bot.py` nella tua home di Termux, ad esempio `$HOME/telegram-tech-news-bot/`.
4. Crea la cartella per i widget (se non esiste):

```bash
mkdir -p $HOME/.shortcuts
```

5. Crea lo script del widget (esempio: `$HOME/.shortcuts/start_tech_news_bot.sh`) con questo contenuto:

```bash
#!/data/data/com.termux/files/usr/bin/sh
# Avvia il bot Telegram Tech News dalla cartella del repository

# Modifica il percorso se hai posizionato il repo altrove
cd "$HOME/telegram-tech-news-bot" || exit 1

# (Opzionale) Esporta qui il token se non l'hai impostato globalmente
# export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjkLMNopQRstuVWxyz"

python3 bot.py
```

6. Rendi eseguibile lo script:

```bash
chmod +x $HOME/.shortcuts/start_tech_news_bot.sh
```

7. Aggiungi il widget Termux:Widget alla schermata principale e seleziona `start_tech_news_bot.sh` come shortcut.

8. Usa il widget: con un tap lo script lancerà `bot.py` in Termux; apri Telegram e premi il pulsante inline per ricevere le notizie. Il bot si chiuderà dopo aver inviato le news.

Note e suggerimenti:

- Se preferisci che il bot resti sempre attivo, puoi eseguire `python3 bot.py` in background con `tmux` o `nohup`, oppure usare Termux:Boot per lanciarlo all'avvio.
- Assicurati che `python3` e le dipendenze (`python-telegram-bot`, `feedparser`) siano installate in Termux:

```bash
pkg install python
pip install python-telegram-bot feedparser
```

---

## Licenza

MIT
