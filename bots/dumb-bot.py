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
shared_data = create_filegen("shared")

# Twitch info here
TWITCH = "https://api.twitch.tv/kraken"
TKEY   = read_key("twitch")
STRAMS = f"{TWITCH}/streams/?game={'{}'}&client_id={TKEY}&limit=1"

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
        logger(f"Error: {ex}")
    return await client.send_message(mobj.channel, "Error: bad input args")

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
        return await client.send_message(mobj.channel, f"https://youtube.com{href}")
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to request the search")

@register_command
async def streams(msg, mobj):
    pass

@register_command
async def clipreg(msg, mobj):
    """
    Register a Twitch.tv username into the Clips registry
    Used to bookmark names to Twitch accounts for ez access
    Must test the urls given to make sure it's a real Twitch account
    Example: !clipreg bulldog admiralbulldog
    """
    pass

@register_command
async def clips(msg, mobj):
    """
    Fetch a clip from a certain registered bookmark
    If no bookmark given (but entries exist), get a random clip
    Example: !clips summit1g
           -> <link to random popular clip>
    """
    pass

@register_command
async def dota_id(msg, mobj):
    """
    Registers a user's Discord ID with a Dota 2 player ID
    This will be used by the automated Dota 2 match parser service
    The string given is tested against OpenDota's API to see if it's valid
    """
    if len(msg) > 30:
        return await client.send_message(mobj.channel, "Bro that's too long")

    r = re_get(f"{OPENDOTA_API}/players/{msg.strip()}")
    if r.status_code != 200:
        return await client.send_message(mobj.channel, "Invalid Dota 2 ID")

    fname = shared_data(f"{mobj.author.id}.dota")
    with open(fname, 'w') as f:
        f.write(msg.strip())

    return await client.send_message(
        mobj.channel,
        "Registered Player ID {msg.strip()}"
    )

# Last step - register events then run
setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end

