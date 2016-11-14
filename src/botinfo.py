#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Packages to use across bot programs
"""

import discord
from discord.ext import commands
import asyncio
from subprocess import getstatusoutput
from time import strftime, localtime
from os import mkdir, listdir
from os.path import isfile, isdir, join
from ast import literal_eval

# Bot local data information
BOT_FOLDER = "botdata"
KEY_FOLDER = "keys"

# shortcut to unpack a syscall from getstatusoutput
call = lambda p: getstatusoutput(p)[1]

# Prefix to use for automating registering commands
bot_prefix = "!"

# a map for all characters in URL search bars to replace
# most search engines replace " " with "+" but for the most
# part it seems to work with either/or '+' or '%20'
char_map = {" ": "%20", "'": "%27", "`": "%60", "%": "%25", "&": "%26",
            "!": "%21", "@": "%40", "#": "%23", "$": "%24", "+": "%2B",
            "*": "%2A", "^": "%5E", "(": "%28", ")": "%29", "=": "%3D",
            "[": "%5B", "]": "%5D", "{": "%7B", "}": "%7D"}

# I'm trying to stop malicious searches from my Pi ;_;
bad_words = ["fuck", "cock", "child", "kiddy", "porn", "pron",
             "masturbate", "shit", "piss", "anal", "cum", "wank"]

def display_url_when_no_servers(client, logger):
    """
    Print a clickable URL when the bot sees no servers active
    This is to defeat the previous method of creating bot links
    """
    if len(client.servers) == 0:
        logger("Link: {}".format(discord.utils.oauth_url(client.user.id)))
    return

def contains_badwords(string):
    """
    Return whether a string contains bad words
    """
    return any([x in string for x in bad_words])

def setup_all_events(client, bot_name, logger, on_r=None, on_e=None, on_m=None):
    """
    Setup all events using default events
    We can pass in custom events to each variable to set those as the events
    The given events have to be named appropriately (on_message, on_ready, on_error)
    """
    if on_r is None:
        client.event(setup_on_ready(client, bot_name, logger))
    elif callable(on_r):
        client.event(on_r)
    if on_e is None:
        client.event(setup_on_error(client, logger))
    elif callable(on_e):
        client.event(on_e)
    if on_m is None:
        client.event(setup_on_message(client, logger))
    elif callable(on_m):
        client.event(on_m)
    return

def setup_on_ready(client, bot_name, logger):
    """
    Automate the on_ready connection process
    """
    async def on_ready():
        if not setup_bot_data(bot_name, logger):
            client.close()
            return logger("Failed to set up {}'s folder".format(bot_name))
        display_url_when_no_servers(client, logger)
        return logger("Connection status: {}".format(client.is_logged_in))
    return on_ready

def setup_on_error(client, logger):
    """
    Automate the on_error process (it's real simple)
    """
    async def on_error(msg, *args, **kwargs):
        return logger("Discord error: {}".format(msg))
    return on_error

def setup_bot_data(bot_name, logger):
    """
    Set up the bot data folder in the root location
    If it can't create the folders, return False
    else return True (so our bot can continue)
    """
    try:
        if not isdir(BOT_FOLDER):
            logger("Setting up root bot folder")
            mkdir(BOT_FOLDER)
        if not isdir(join(BOT_FOLDER, bot_name)):
            logger("Setting up {} data folder".format(bot_name))
            mkdir(join(BOT_FOLDER, bot_name))
    except Exception as ex:
        logger("Fail: {}".format(ex))
        return False
    return True

def register_command(func=None, binds={}):
    """
    We're gonna use some real bad behavior
    We're going to store binds inside of the function's default arg
    When the function is passed None, we return the binds
    When we pass a function, we register it to the binds
    Else we return the function we were originally given so
    we can ensure it acts as a wrapper of the given function
    """
    if callable(func):
        if func.__name__ not in binds:
            binds["{}{}".format(bot_prefix, func.__name__)] = func
    elif func is None:
        return binds
    return func

def setup_on_message(client, logger):
    """
    Create a basic on_message function to use
    """
    async def on_message(msg):
        if contains_badwords(msg.content.lower()):
            return
        splits = msg.content.strip().split(" ")
        key = splits.pop(0).lower()
        rest = " ".join(splits) if len(splits) > 0 else ""
        args = [rest, msg]
        binds = register_command()
        if key in binds:
            if rest.lower().startswith("help"):
                return await client.send_message(msg.channel, pre_text(binds[key].__doc__))
            return await binds[key](*args)
        return
    return on_message

def read_key(bot_name):
    """
    Read a key file which contains bot tokens
    Return false if the key couldn't be read
    """
    try:
        with open(join(KEY_FOLDER, "{}.key".format(bot_name)), 'r') as f:
            return f.read()
    except Exception:
        raise IOError("Can't read key")
    return False

def pre_text(string):
    """
    Encapsulate a string inside a Markdown <pre> container
    """
    return "```{}```".format(string.rstrip().strip("\n").replace("\t", ""))

def url_replace(string, cmap=char_map):
    """
    Safely replace characters with URL friendly characters
    Optional: feed in a character map to use (defaults to predefined)
    """
    s = string
    for k, v in cmap.items():
        s.replace(k, v)
    return s

def bot_folder(bot_name):
    """
    Return the path to the bot's data folder
    ie: bot_folder("dumb-bot") -> botdata/dumb-bot
    """
    return join(BOT_FOLDER, bot_name)

def read_lines(file_name):
    """
    Read all the lines in a given file
    Shortcut to avoid clumping up of many with-blocks
    Handles the IO exception to return a blank list when no file is present
    """
    lines = []
    try:
        with open(file_name, "r") as f:
            lines = f.readlines()
    except Exception:
        pass
    finally:
        return lines

def create_filegen(bot_name):
    """
    Create a function which allows quick path joins
    to interact with files in a Bot's folder
    """
    def bot_file(filename):
        return join(BOT_FOLDER, bot_name, filename)
    return bot_file

def create_logger(bot_name):
    """
    Create a logger func to yield messages from bots
    Color is generated by sum([ord(x) for x in name])
    """
    color = 16 + (sum([ord(c) for c in bot_name]) % 240)
    def logger(msg):
        print("[\033[38;5;{3}m{0:<12}\033[0m @ {1}] {2}".format(
            bot_name, strftime("%H:%M:%S", localtime()), msg, color))
        return True
    return logger

# One function to bind them all (it's a bot runner)
def run_the_bot(client, bot_name, loggy):
    """
    Abstract to keep the bot running function in one place
    Only works when each bot uses the same Client type object
    """
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.start(read_key(bot_name)))
    except Exception as e:
        loggy("Whoop! {}".format(e))
    except SystemExit:
        loggy("SystemExit, quitting")
    except KeyboardInterrupt:
        loggy("Keyboard Int, quitting")
    finally:
        loggy("Exiting")
        loop.run_until_complete(client.logout())
        loop.stop()
        loop.close()
        quit()

# end
