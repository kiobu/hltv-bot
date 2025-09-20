import datetime
import asyncio
from typing import List
from typing_extensions import deprecated

import discord
import feedparser
from dateutil.parser import parse
from consts import Consts, Site

intents = discord.Intents.default()
# intents.message_content = True

client = discord.Client(intents=intents)


@deprecated
def get_guid(guid_str: str) -> int:
    return int(''.join(filter(str.isdigit, guid_str)))


def get_last_article_timestamp(site: Site) -> str:
    try:
        with open(f'../{site}_last_article_timestamp.txt', 'r') as txt:
            try:
                return txt.readline()
            except ValueError:
                return str(0)
    except FileNotFoundError:
        set_last_article_timestamp(site, "Mon, 1 Jan 1970 01:00:00 -0500")
        return "Mon, 1 Jan 1970 01:00:00 -0500"


def set_last_article_timestamp(site: Site, ts: str):
    with open(f'../{site}_last_article_timestamp.txt', 'w+') as txt:
        txt.write(ts)


def log(msg: str):
    print(f"[{datetime.datetime.now()}]: {msg}")


def debug_log(msg: str):
    if Consts.DEBUG:
        print(f"[{datetime.datetime.now()}][DEBUG]: {msg}")

async def poll(channels: List[discord.TextChannel]):
    feeds = None
    try:
        feeds = {
            Site.HLTV: feedparser.parse(Consts.HLTV_RSS_FEED),
            # Site.DUST_2: feedparser.parse(Consts.D2_RSS_FEED)
        }
    except Exception as e:
        log(f"Could not parse RSS feeds: {str(e)}")

    if not feeds:
        return

    for _i, site in enumerate(feeds):
        latest_article = None
        try:
            latest_article = feeds[site].entries[0]
        except Exception as e:
            log(f"Could not find article for some reason, RSS feed: {feeds[site]}")

        if not latest_article:
            return

        if parse(latest_article.published) > parse(get_last_article_timestamp(site)):
            # new article, publish.
            log(f"New {site} article in RSS feed.")

            embed = discord.Embed(
                color=discord.Color.dark_blue(),
                title=f"[{site}] {latest_article.title}",
                description=latest_article.description,
                url=Consts.ARTICLE_TPL.format(DOMAIN=site, ID=get_guid(latest_article.guid))
            )

            # attach image to embed if exists
            try:
                embed.set_image(url=latest_article['media_content'][0]['url'])
            except KeyError:
                pass

            debug_log(f"Article timestamp: {latest_article.published}")
            debug_log(f"Article title: {latest_article.title}")

            for channel in channels:
                try:
                    await channel.send(embed=embed)
                    log(f"Embed created and sent to channel: '{channel.name}'")
                except Exception as e:
                    log(f"Error sending message to channel '{channel.name}': {str(e)}")

            set_last_article_timestamp(site, latest_article.published)

        else:
            debug_log(f"Polled, but latest article found is older or the same as current.\n--> Latest: {latest_article.published}\n--> Cached: {get_last_article_timestamp(site)}")


@client.event
async def on_ready():
    log(f'Client initialized as {client.user}.')

    while True:
        await poll([client.get_channel(ch_id) for ch_id in Consts.CHANNEL_IDS])
        await asyncio.sleep(Consts.POLL_RATE_SEC)

client.run(Consts.TOKEN)
