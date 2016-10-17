#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from random import randint, choice

help_msg = """A Bot that doesn't do a whole lot
https://github.com/sleibrock/discord-bots/blob/master/bot-command-guide.md
"""

bot_name = "dumb-bot"
client = commands.Bot(command_prefix=".", description=help_msg)
logger = create_logger(bot_name)

@client.event
async def on_ready():
    """
    The function that is consumed upon startup
    Set vars, check for bot folder existence, etc
    """
    if not setup_bot_data(bot_name, logger):
        client.close()
        return logger("Failed to set up {}'s folder".format(bot_name))
    return logger("Connection status: {}".format(client.is_logged_in))

@client.event
async def on_error(msg, *args, **kwargs):
    return logger("Discord error: {}".format(msg))

@client.command()
async def commits():
    """Print out a `git log --graph --decorate=short --oneline | head -n 5`"""
    return await client.say(pre_text(call("git log --decorate=full --graph --oneline | head -n 5")))

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
    logger("Killing own thread for upgrade")
    client.close()
    return quit()

@client.command()
async def rtd(*string):
    """
    Roll a d<N> di[c]e <X> number of times
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

@client.command()
async def osfrog(*args):
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
    return await client.say(choice(data))

if __name__ == "__main__":
    try:
        key = argv[1]
        client.run(read_key(key))
    except Exception as e:
        logger("Whoops! {}".format(e))
    except SystemExit:
        logger("Leaving this existence behind")
    except KeyboardInterrupt:
        logger("Ouch!")
    finally:
        logger("Exiting\n")
    quit()

# end

