#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Dumb-bot

The dumbest bot of them all
Mostly a collection of scraping utilities and 
otherwise non-related functions
"""

from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from random import randint, choice

help_msg = """
The Discord Bot Project
https://github.com/sleibrock/discord-bots

Command reference
https://github.com/sleibrock/discord-bots/blob/master/docs/bot-command-guide.md
"""

bot_name = "dumb-bot"
client = discord.Client()
logger = create_logger(bot_name)

@register_command
async def howto(msg, mobj):
    """
    Return a help message
    If you came here from !howto help; there's nothing else, sorry
    """
    return await client.send_message(mobj.channel, pre_text(help_msg))

@register_command
async def rtd(msg, mobj):
    """
    Roll a d<N> di[c]e <X> number of times
    Example: !rtd 2d10 - rolls two d10 dice
    """
    if msg == "":
        return await client.send_message(mobj.channel, "You didn't say anything!")
    try:
        times, sides = list(map(int, msg.lower().split("d")))
        res = [randint(1, sides) for x in range(times)]
        return await client.send_message(mobj.channel, ", ".join(map(str, res)))
    except Exception as ex:
        logger("Error: {}".format(ex))
    return await client.send_message(mobj.channel, "Error: bad input args")

@register_command
async def ddg(msg, mobj):
    """
    Search DuckDuckGo and post the first result
    Example: !ddg let me google that for you
    """
    try:
        if msg == "":
            return await client.send_message(mobj.channel, "You didn't search for anything!")
        msg.replace(" ", "%20") # replace spaces
        url = "https://duckduckgo.com/html/?q={0}".format(msg)
        bs = BS(re_get(url).text, "html.parser")
        results = bs.find_all("div", class_="web-result")
        if not results:
            return await client.send_message(mobj.channel, "Couldn't find anything")
        a = results[0].find("a", class_="result__a")
        title, link = a.text, a["href"]
        return await client.send_message(mobj.channel, "{} - {}".format(title, link))
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to get the search")

@register_command
async def yt(msg, mobj):
    """
    Do a youtube search and yield the first result
    Example: !yt how do I take a screenshot
    """
    try:
        if msg == "":
            return await client.send_message(mobj.channel, "You didn't search for anything!")
        msg.replace(" ", "+")
        url = "https://www.youtube.com/results?search_query={}".format(msg)
        bs = BS(re_get(url).text, "html.parser")
        items = bs.find("div", id="results").find_all("div", class_="yt-lockup-content")
        if not items:
            return await client.send_message(mobj.channel, "Couldn't find any results")

        # Search for a proper youtube url, has to start with /watch
        # TODO: rewrite this with a list comp/filter
        i, found = 0, False
        while not found and i < 20:
            href = items[i].find("a", class_="yt-uix-sessionlink")["href"]
            if href.startswith("/watch"):
                found = True
            i += 1
        if not found:
            return await client.send_message(mobj.channel, "Couldn't find a link")
        return await client.send_message(mobj.channel, "https://youtube.com{}".format(href))
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to request the search")

# Last step - register events then run
setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end

