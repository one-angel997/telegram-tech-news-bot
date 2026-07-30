#!/data/data/com.termux/files/usr/bin/sh
# Script di esempio per Termux:Widget che avvia il Telegram Tech News Bot.
# Salva questo file in ~/.shortcuts/start_tech_news_bot.sh e rendilo eseguibile (chmod +x).

cd "$HOME/telegram-tech-news-bot" || exit 1
# (Opzionale) Se non usi la variabile d'ambiente globale puoi impostare qui il token:
# export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjkLMNopQRstuVWxyz"

python3 bot.py
