import os

os.environ.setdefault("BOT_PROFILE", "tech_news")

from app.telegram.bot import main

if __name__ == "__main__":
    main()
