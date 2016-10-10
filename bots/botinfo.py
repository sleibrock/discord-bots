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
from time import strftime, gmtime
from os import mkdir, listdir
from os.path import isfile, isdir, join

# Bot local data information
BOT_FOLDER = "botdata"

# shortcut to unpack a syscall from getstatusoutput
call = lambda p: getstatusoutput(p)[1]

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
    """Read a key file which contains bot tokens"""
    with open(filename, 'r') as f:
        return f.read()

def pre_text(string):
    return "```{}```".format(string)

def debug_message(msg):
    return pre_text("From: {}\nChannel: {}\nMessage: {}".format(msg.author, msg.channel, msg.content))

def bot_folder(bot_name):
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

    [dumb-bot: 10:32:48] I crashed
    [another-bot: 10:32:49] I didn't
    """
    def log_func(data_string):
        print("[{}: {}] {}".format(bot_name, strftime("%H:%M:%S", gmtime()), data_string))
    return log_func
        
