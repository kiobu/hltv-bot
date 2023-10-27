import enum


class Consts:
    HLTV_RSS_FEED: str = "https://hltv.org/rss/news"
    D2_RSS_FEED: str = "https://dust2.us/rss"
    ARTICLE_TPL: str = "https://www.{DOMAIN}/news/{ID}/article"
    POLL_RATE_SEC: int = 300
    CHANNEL_ID: int = 859850906513440791
    TOKEN: str = ""


class Site:
    HLTV: str = "HLTV.ORG"
    DUST_2: str = "DUST2.US"
