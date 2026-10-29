import feedparser


def fetch_feed(feed_url: str):
    return feedparser.parse(feed_url)
