#!/data/data/com.termux/files/usr/bin/sh
# Script di esempio per Termux:Widget che avvia il Telegram Tech News Bot.
# Salva questo file in ~/.shortcuts/start_tech_news_bot.sh e rendilo eseguibile (chmod +x).

cd "$HOME/telegram-tech-news-bot" || exit 1

if [ ! -x .venv/bin/python ]; then
  echo "Ambiente Python non trovato. Segui la sezione di installazione del bot nel README." >&2
  exit 1
fi

exec .venv/bin/python bot.py
