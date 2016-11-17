#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Hacker bot

Requires: cowsay installed on system
"""

from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from random import choice

bot_name = "hacker-bot"
client   = discord.Client()
logger   = create_logger(bot_name)
bot_data = create_filegen(bot_name)
max_slen = 300
max_data = 100
max_stak = 10
            
@register_command
async def test(msg, mobj):
    print(client.messages)
    print(len(client.messages))
    print("last message was: {}".format(get_last_message(mobj.channel).content))
    return await client.send_message(mobj.channel, "test")

@register_command
async def uptime(msg, mobj):
    """
    Return the uptime of the host system
    """
    return await client.send_message(mobj.channel, pre_text(call("uptime")))

@register_command
async def free(msg, mobj):
    """
    Return how much memory is free
    """
    return await client.send_message(mobj.channel, pre_text(call("free -m")))

@register_command
async def vmstat(msg, mobj):
    """
    Return raw memory stats from `vmstat`
    """
    return await client.send_message(mobj.channel, pre_text(call("vmstat")))

@register_command
async def uname(msg, mobj):
    """
    Return `uname -a` showing system and kernel version
    """
    return await client.send_message(mobj.channel, pre_text(call("uname -a | cowsay")))

@register_command
async def cal(msg, mobj):
    """
    Return the current month calendar
    """
    return await client.send_message(mobj.channel, pre_text(call("cal")))

@register_command
async def sed(msg, mobj):
    """
    Sed the previous user's message (as opposed to just editing it)
    Example: !sed s/hi/hello/g
    """
    if msg == "":
        return
    auth = mobj.author.id
    chan = mobj.channel
    last_m = get_last_message(client, chan, auth).content.strip().replace("\"", "'")
    return await client.send_message(chan, pre_text(call("echo \"{}\" | sed -s {}".format(last_m, msg))))

# The Git section
@register_command
async def update(msg, mobj):
    """
    Execute a `git pull` to update the code
    If there was a successful pull, the bot will quit and be restarted later
    Example: !update
    """
    print(msg)
    result = call("git pull")
    await client.send_message(mobj.channel, pre_text(result))
    if result.strip() == "Already up-to-date.":
        return
    logger("Restarting self")
    client.close()
    return quit()

@register_command
async def commits(msg, mobj):
    """
    Execute a `git log --oneline --graph --decorate=short | head -n 5`
    Example: !commits
    """
    return await client.send_message(
        mobj.channel, pre_text(call("git log --oneline --graph --decorate=short | head -n 5")))

# The Cowsay section for cowtagging and cowsay
@register_command
async def cowtag(msg, mobj):
    """
    Find the message before this one and add it to our cow list
    Example: !cowtag
    """
    chan = mobj.channel
    cowlist = bot_data("{}.txt".format(chan.id))
    last_m = get_last_message(client, chan)
    if last_m is None:
        return await client.send_message(chan, "Couldn't tag last message")
    last_m = last_m.content.replace("\n", " ").replace("\r", " ").strip()[:max_slen]
    last_m = last_m.replace("\"", "'")
    lines = read_lines(cowlist)
    lines.append(last_m)
    if len(lines) > max_data:
        lines.pop(0)
    if not write_lines(cowlist, lines):
        return await client.send_message(chan, "Error writing to file")
    return await client.send_message(chan, "Bagged and tagged")

@register_command
async def cowsay(msg, mobj):
    """
    Return a random cowsay message
    Example: !cowsay
    """
    chan = mobj.channel.id
    cowlist = bot_data("{}.txt".format(chan))
    cowlines = read_lines(cowlist)
    if not cowlines:
        return await client.send_message(mobj.channel, "No cow messages here")
    rand = choice(cowlines)
    if rand.strip() == "":
        return await client.send_message(mobj.channel, "No cow messages here")
    return await client.send_message(mobj.channel, pre_text(call("echo \"{}\" | cowsay".format(rand))))

setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)
