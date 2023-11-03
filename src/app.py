import datetime
import asyncio

import discord
import feedparser
from dateutil.parser import parse
from consts import Consts, Site

intents = discord.Intents.default()
# intents.message_content = True

client = discord.Client(intents=intents)


def get_guid(guid_str: str) -> int:
    """ deprecated """
    return int(''.join(filter(str.isdigit, guid_str)))


def get_last_article_timestamp(site: Site) -> str:
    try:
        with open(f'../{site}_last_article_timestamp.txt', 'r') as txt:
            try:
                return txt.readline()
            except ValueError:
                return str(0)
    except FileNotFoundError:
        set_last_article_timestamp(site, "0")
        return "0"


def set_last_article_timestamp(site: Site, ts: str):
    with open(f'../{site}_last_article_timestamp.txt', 'w+') as txt:
        txt.write(ts)


def log(msg: str):
    print(f"[{datetime.datetime.now()}]: {msg}")


async def poll(channel: discord.TextChannel):
    feeds = {
        Site.HLTV: feedparser.parse(Consts.HLTV_RSS_FEED),
        Site.DUST_2: feedparser.parse(Consts.D2_RSS_FEED)
    }

    for _i, site in enumerate(feeds):
        latest_article = feeds[site].entries[0]

        if parse(latest_article.published) > parse(get_last_article_timestamp(site)):
            # new article, publish.
            log(f"New {site} article in RSS feed.")

            embed = discord.Embed(
                color=discord.Color.dark_blue(),
                title=f"[{site}] {latest_article.title}",
                description=latest_article.description,
                url=Consts.ARTICLE_TPL.format(DOMAIN=site,ID=get_guid(latest_article.guid))
            )

            if Consts.DEBUG:
                log(f"Article timestamp: {latest_article.published}")
                log(f"Article title: {latest_article.title}")

            await channel.send(embed=embed)
            log("Embed created and sent to guild channel.")

            set_last_article_timestamp(site, latest_article.published)

        else:
            if Consts.DEBUG:
                log(f"Polled, but latest article found is older or the same as current.\n--> Latest: {latest_article.published}\n--> Cached: {get_last_article_timestamp(site)}")


@client.event
async def on_ready():
    log(f'Client initialized as {client.user}.')

    while True:
        await poll(client.get_channel(Consts.CHANNEL_ID))
        await asyncio.sleep(Consts.POLL_RATE_SEC)

client.run(Consts.TOKEN)
