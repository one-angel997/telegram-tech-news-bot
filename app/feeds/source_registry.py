from app.common.config import get_config


def get_feed_urls():
    config = get_config()
    return config.get("feeds", [])


def get_categories():
    config = get_config()
    return config.get("categories", {})
