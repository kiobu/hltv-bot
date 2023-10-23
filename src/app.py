import datetime
import asyncio

import discord
import feedparser
from consts import Consts

intents = discord.Intents.default()
# intents.message_content = True

client = discord.Client(intents=intents)


def get_guid(guid_str: str) -> int:
    return int(''.join(filter(str.isdigit, guid_str)))


def get_last_article_guid() -> int:
    with open('../last_article_guid.txt', 'r') as txt:
        try:
            return int(txt.readline())
        except ValueError:
            return 0


def set_last_article_guid(guid: int):
    with open('../last_article_guid.txt', 'w') as txt:
        txt.write(str(guid))


def log(msg: str):
    print(f"[{datetime.datetime.now()}]: {msg}")


async def poll(channel: discord.TextChannel):
    feed = feedparser.parse(Consts.RSS_FEED)
    latest_article = feed.entries[0]

    if get_guid(latest_article.guid) > get_last_article_guid():
        # new article, publish.
        log("New article in RSS feed.")

        embed = discord.Embed(
            title=latest_article.title,
            description=latest_article.description,
            url=Consts.ARTICLE_TPL.format(ID=get_guid(latest_article.guid))
        )

        await channel.send(embed=embed)
        log("Embed created and sent to guild channel.")

        set_last_article_guid(get_guid(latest_article.guid))


@client.event
async def on_ready():
    log(f'Client initialized as {client.user}.')

    while True:
        await poll(client.get_channel(Consts.CHANNEL_ID))
        await asyncio.sleep(Consts.POLL_RATE_SEC)

client.run(Consts.TOKEN)
