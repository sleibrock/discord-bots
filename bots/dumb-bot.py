#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from random import randint, choice

help_msg = """A Bot that doesn't do a whole lot
https://github.com/sleibrock/discord-bots/blob/master/docs/bot-command-guide.md
"""

bot_name = "dumb-bot"
client = discord.Client()
logger = create_logger(bot_name)

@register_command
async def howto(msg, mid, mch):
    """Return a help message"""
    return await client.send_message(mch, pre_text(help_msg))

@register_command
async def free(msg, mid, mch):
    """Return a printout of `free -m` to see memory available"""
    return await client.send_message(mch, pre_text(call("free -m")))

@register_command
async def commits(msg, mid, mch):
    """Print out a `git log --graph --decorate=short --oneline | head -n 5`"""
    return await client.send_message(mch, pre_text(call("git log --decorate=short --graph --oneline | head -n 5")))

@register_command
async def update(msg, mid, mch):
    """
    Execute a `git pull` to update the code
    If there was a successful pull, dumb-bot will restart his own thread
    """
    # TODO: detect files updated and kill their respected threads?
    result = call("git pull")
    await client.send_message(mch, pre_text(result))
    if result.strip() == "Already up-to-date.": # figure out something non-string-comp
        return
    await client.send_message(mch, "Upgrading myself senpai")
    logger("Killing own thread for upgrade")
    client.close()
    return quit()

@register_command
async def rtd(msg, mid, mch):
    """
    Roll a d<N> di[c]e <X> number of times
    Example: .rtd 2d10 - rolls two d10 dice
    """
    if msg == "":
        return await client.send_message(mch, "You didn't say anything!")
    try:
        times, sides = list(map(int, msg.lower().split("d")))
        res = [randint(1, sides) for x in range(times)]
        return await client.send_message(mch, ", ".join(map(str, res)))
    except Exception as ex:
        logger("Error: {}".format(ex))
    return await client.send_message(mch, "Error: bad input args")

@register_command
async def ddg(msg, mid, mch):
    """
    Search DuckDuckGo and post the first result
    Example: .ddg let me google that for you
    """
    try:
        if msg == "":
            return await client.send_message(mch, "You didn't search for anything!")
        msg.replace(" ", "%20") # replace spaces
        url = "https://duckduckgo.com/html/?q={0}".format(msg)
        bs = BS(re_get(url).text, "html.parser")
        results = bs.find_all("div", class_="web-result")
        if not results:
            return await client.send_message(mch, "Couldn't find anything")
        a = results[0].find("a", class_="result__a")
        title, link = a.text, a["href"]
        return await client.send_message(mch, "{} - {}".format(title, link))
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.send_message(mch, "Failed to get the search")

@register_command
async def yt(msg, mid, mch):
    """
    Do a youtube search and yield the first result
    Example: .yt how do I take a screenshot
    """
    try:
        if msg == "":
            return await client.send_message(mch, "You didn't search for anything!")
        msg.replace(" ", "+")
        url = "https://www.youtube.com/results?search_query={}".format(msg)
        bs = BS(re_get(url).text, "html.parser")
        items = bs.find("div", id="results").find_all("div", class_="yt-lockup-content")
        if not items:
            return await client.send_message(mch, "Couldn't find any results")

        # Search for a proper youtube url, has to start with /watch
        i, found = 0, False
        while not found and i < 20:
            href = items[i].find("a", class_="yt-uix-sessionlink")["href"]
            if href.startswith("/watch"):
                found = True
            i += 1
        if not found:
            return await client.send_message(mch, "Couldn't find a link")
        return await client.send_message(mch, "https://youtube.com{}".format(href))
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.send_message(mch, "Failed to request the search")

@register_command
async def wa(msg, mid, mch):
    """
    Return a link to a Wolfram Alpha search
    Doesn't do anything special
    """
    return await client.send_message(mch, "Not implemented yet")

@register_command
async def osfrog(msg, mid, mch):
    """
    Yet another command that is temporary
    """
    data = [":frog: BALANCE IN ALL THINGS :frog:",
            ":thumbsup: Thanks Purge :thumbsup:",
            ":frog: :gun:",
            ":frog: le balanced :fish: man :frog:",
            ":frog: +1 :shield: armor :frog:",
            ":frog: :dragon: Illusory orb speed increased by 1 :frog:",
            ":frog: Vacuum cooldown rescaled from 28.0 seconds to 28 seconds :frog:",
            ":frog: le balanced :cloud_tornado: man :frog:",
            ":frog: SEEMS GOOD TO ME :frog:",
            ":frog: le balanced 1050 :dragon: lance attack range :frog:",
            ":frog: ¯\_(ツ)_/¯ :frog:",]
    return await client.send_message(mch, choice(data))

# Last step - register events then run
setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end

