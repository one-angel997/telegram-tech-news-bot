import os

# Default runtime profile: use the shared bot layer.
# You can override with:
#   BOT_PROFILE=f1_news python bot.py
os.environ.setdefault("BOT_PROFILE", "tech_news")

from app.telegram.bot import main

if __name__ == "__main__":
    main()
