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
from os import mkdir
from os.path import isdir, join

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
            logger("Setting up {} data folder")
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
        
