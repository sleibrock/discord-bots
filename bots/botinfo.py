#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Packages to use across bot programs
"""

import discord
from discord.ext import commands
import asyncio
from sys import argv
from subprocess import getstatusoutput
from time import strftime, localtime
from os import mkdir, listdir
from os.path import isfile, isdir, join
from ast import literal_eval

# Bot local data information
BOT_FOLDER = "botdata"

# shortcut to unpack a syscall from getstatusoutput
call = lambda p: getstatusoutput(p)[1]

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

# This will probably never catch all the things I really want to stop
bad_code = ["while", "for", "import", "lambda", "eval", "exec", "compile",
            "*", "+", "-", "/", "_", "raise", "Exception", ]

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

def setup_bot_data(bot_name, logger):
    """
    Set up the bot data folder in the root location
    If if can't create the folders, return False
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

def read_key(filename):
    """
    Read a key file which contains bot tokens
    Return false if the key couldn't be read
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except Exception:
        pass
    return False

def pre_text(string):
    """
    Encapsulate a string inside a Markdown <pre> container
    """
    return "```{}```".format(string.rstrip().strip("\n"))

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
    This sets up a logger to be used in the bot threading
    this ambiguates bot output as to see which bot crashes
    rather than output being boggled together

    [dumb-bot:     10:32:48] I crashed
    [another-bot:  10:32:49] I didn't
    """
    def log_func(data_string):
        print("[{0:<12} {1}] {2}".format("{}:".format(bot_name), strftime("%H:%M:%S", localtime()), data_string))
    return log_func

# One function to bind them all (it's a bot runner)
def run_the_bot(client, argv, loggy):
    """
    Abstract to keep the bot running function in one place
    Only works when each bot uses the same Client type object
    """
    try:
        key = argv[1]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.start(read_key(key)))
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
