# 📡 Telegram Tech News Bot

Un bot Telegram scritto in **Python**, pensato per girare anche in **Termux** su Android, che recupera le ultime notizie tecnologiche da fonti italiane come **HDblog, SmartWorld, Hardware Upgrade, Tom’s Hardware, Everyeye, Wired Italia**.

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
- **Termux** (opzionale, per esecuzione su Android)

---

## 📲 Creazione del bot su Telegram

1. Apri Telegram.
2. Cerca **@BotFather**.
3. Esegui il comando:

   ```text
   /newbot
4.Scegli un nome per il bot (es. Tech News Bot).
   Scegli un username che termini con bot (es. tech_news_bot).

5. BotFather ti fornirà un TOKEN simile a:   
   1234567890:ABCdefGHIjkLMNopQRstuVWxyz
   
7. Inserisci il token nel file bot.py:
   TOKEN = "INSERISCI_IL_TUO_TOKEN_TELEGRAM"
   oppure esportalo come variabile d'ambiente:
   export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjkLMNo
