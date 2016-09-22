#!/usr/bin/env python
#-*- coding: utf-8 -*-

from functions import *

bot_name = "dumb-bot"
client = commands.Bot(command_prefix=".")
logger = create_logger(bot_name)

@client.event
async def on_ready():
    return logger("Connection status: {}".format(client.is_logged_in))

@client.command()
async def source():
    """Print out a link to the source code"""
    return await client.say("https://github.com/sleibrock/discord-bots")

@client.command()
async def commits():
    """Print out a `git log --oneline | head -n 5`"""
    return await client.say(pre_text(call("git log --oneline | head -n 5")))

@client.command()
async def update():
    """Execute a `git pull` to update the code (doesn't restart VMs)"""
    return await client.say(pre_text(call(["git pull"])))

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
async def e(*expression):
    """
    Evaluate an expression with Python syntax
    Imports are not allowed in eval expressions
    """
    s = " ".join(expression)
    print(expression)
    print(s)
    if len(expression) > 80:
        return await client.say("Input was too large, sorry")
    try:
        await client.say(eval(s))
    except Exception as ex:
        await client.say("Error: {}".format(ex))
    return

if __name__ == "__main__":
    argv.pop(0)
    key = argv.pop(0)
    client.run(read_key(key))

