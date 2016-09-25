#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
from math import sqrt, sin, cos, tan, pow, exp, pi, ceil, floor, e, factorial, log, log2
from math import radians, degrees, acos, asin, atan, atan2, erf, gamma, gcd
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from random import randint
from os import mkdir
from os.path import isdir, join

bot_name = "dumb-bot"
client = commands.Bot(command_prefix=".", description="A bot that doesn't do a whole lot")
logger = create_logger(bot_name)

@client.event
async def on_ready():
    """
    The function that is consumed upon startup
    Set vars, check for bot folder existence, etc
    """
    if not setup_bot_data(bot_name, logger):
        logger("Failed to set up {}'s folder".format(bot_name))
        client.close()
    return logger("Connection status: {}".format(client.is_logged_in))

@client.command()
async def source():
    """Print out a link to the source code"""
    return await client.say("https://github.com/sleibrock/discord-bots")

@client.command()
async def commits():
    """Print out a `git log --graph --decorate=full --oneline | head -n 5`"""
    return await client.say(pre_text(call("git log --decorate=full --graph --oneline | head -n 5")))

@client.command()
async def authors():
    """Return a `git shortlog -sn` output to print authors"""
    return await client.say(pre_text(call("git shortlog -sn")))

@client.command()
async def update():
    """
    Execute a `git pull` to update the code 
    If there was a successful pull, dumb-bot will restart his own thread
    """
    # TODO: detect files updated and kill their respected threads?
    result = call("git pull")
    await client.say(pre_text(result))
    if result.strip() == "Already up-to-date.": # figure out something non-string-comp
        return
    await client.say("Upgrading myself senpai")
    client.close()
    return logger("Killing own thread for upgrade")

@client.command()
async def uname():
    """Return the system info of the host"""
    return await client.say(pre_text(call("uname -a")))
    
@client.command()
async def uptime():
    """Return the uptime of the host machine"""
    return await client.say(pre_text(call(["uptime"])))

@client.command()
async def free():
    """See how much memory is available"""
    return await client.say(pre_text(call(["free"])))

@client.command()
async def servers():
    """See the servers the bot is connected to"""
    return await client.say(pre_text(", ".join(map(str, client.servers))))

@client.command()
async def rtd(*string):
    """
    Roll a d<N> die <X> number of times
    Example: .rtd 2d10 - rolls two d10 dice
    """
    dice_str = "".join(string).strip()
    logger(dice_str)
    if dice_str == "":
        return await client.say("You didn't say anything!")
    try:
        times, sides = list(map(int, dice_str.lower().split("d")))
        logger("roll {} d{}".format(times, sides))
        res = [randint(1, sides) for x in range(times)] 
        return await client.say(", ".join(map(str, res)))
    except Exception as ex:
        logger("Error: {}".format(ex))
    return await client.say("Error: bad input arg")

@client.command()
async def ddg(*search):
    """
    Search DuckDuckGo and post the first result
    Example: .ddg let me google that for you
    """
    try:
        search_str = " ".join(search)
        if search_str.strip() == "":
            return await client.say("You didn't search for anything!")
        search_str.replace(" ", "%20") # replace spaces
        url = "https://duckduckgo.com/html/?q={0}".format(search_str)
        bs = BS(re_get(url).text, "html.parser")
        results = bs.find_all("div", class_="web-result")
        if not results:
            return await client.say("Couldn't find anything")
        a = results[0].find("a", class_="result__a")
        title = a.text
        link = a["href"]
        return await client.say("{} - {}".format(title, link))
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.say("Failed to get the search")

@client.command()
async def yt(*search):
    """
    Do a youtube search and yield the first result
    Example: .yt how do I take a screenshot
    """
    try:
        search_str = " ".join(search).lower()
        if search_str.strip() == "":
            return await client.say("You didn't search for anything!")
        search_str.replace(" ", "+")
        url = "https://www.youtube.com/results?search_query={}".format(search_str)
        bs = BS(re_get(url).text, "html.parser")
        items = bs.find("div", id="results").find_all("div", class_="yt-lockup-content")
        if not items:
            return await client.say("Couldn't find any results")

        # Search for a proper youtube url, has to start with /watch
        i, found = 0, False
        while not found and i < 20:
            href = items[i].find("a", class_="yt-uix-sessionlink")["href"]
            if href.startswith("/watch"):
                found = True
            i += 1
        if not found:
            return await client.say("Couldn't find a link")
        return await client.say("https://youtube.com{}".format(href))
    except Exception as ex:
        logger("Fail: {}".format(ex))
    return await client.say("Failed to request the search")

if __name__ == "__main__":
    try:
        argv.pop(0)
        key = argv.pop(0)
        client.run(read_key(key))
    except Exception as e:
        logger("Whoops! {}".format(e))
    except SystemExit:
        logger("Leaving this existence behind")
    except KeyboardInterrupt:
        logger("Ouch!")
    quit()

# end

