from app.common.config import get_config


def get_generic_feed_urls():
    """Return shared feeds used for every category and for the all-news view."""
    config = get_config()
    feeds = config.get("feeds", {})
    if isinstance(feeds, list):
        # Backward compatibility with profiles using the old flat feed list.
        return feeds
    return feeds.get("generic", [])


def get_category_feed_urls(category_id: str):
    """Return specialist feed URLs configured for a category."""
    if category_id == "all":
        return []
    categories = get_categories()
    category = categories.get(category_id, {})
    return category.get("feeds", [])


def get_feed_urls(category_id: str = "all"):
    """Return generic feeds and, when selected, the category's specialist feeds."""
    urls = get_generic_feed_urls() + get_category_feed_urls(category_id)
    return list(dict.fromkeys(urls))


def get_categories():
    config = get_config()
    return config.get("categories", {})
