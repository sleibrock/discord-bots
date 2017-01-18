#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Dota bot

Utility functions for dota-related activities
"""

from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get

# build a static list of heroes/items here
# Instead of waiting on a net request, just write them all
HEROES = []

# Boots to pick from
BOOTS = [
    "Phase Boots",
    "Tranquil Boots",
    "Power Treads",
    "Boots of Travel",
    "Guardian Greaves",
]

ITEMS = [
    "Glimmer Cape",
    "Hurricane Pike",
    "Bloodthirster",
    "Daedelus",
    "Satanic",
    "Aether Lens",
    "Echo Saber",
    "Monkey King Bar",
    "Black King Bar",
    "Blink Dagger",
    "Aghanim's Scepter",
    "Bloodstone",
    "Lotus Orb",
    "Linken's Sphere",
    "Radiance",
    "Butterfly",
    "Moon Shard",
    "Eye of Skadi",
    "Crimson Guard",
]

bot_name = "dota-bot"
client = discord.Client()
logger = create_logger(bot_name)

def get_latest_video(youtube_id):
    """
    Retrieve the latest video from a YouTube user via scraping
    """
    pass

@register_command
async def osfrog(msg, mobj):
    """
    Patch 7.02: help string was removed from Captain's Mode 
    """
    return

@register_command
async def challenge(msg, mobj):
    """
    The Challenge
    Picks a random Dota Two hero, boots, and three items you must buy
    RULES: if you fail to meet the challenge, you lose coolness
    (Only takes into consideration med-high tier items (no gloves)
    Example: !challenge
             -> Bloodseeker: Mana, Mekansm, Dagon, Glimmer Cape
    """
    return

@register_command
async def register(msg, mobj):
    """
    Register's a user's Discord ID and associates it with a Dota ID
    This is used to retrieve a user's last played match from OpenDota 
    """
    return

@register_command
async def lastmatch(msg, mobj):
    """
    Fetch a user's ID from the FS and yield the last played match
    from the OpenDota API
    The user must first associate a Dota ID with !register to use this
    """
    return

@register_command
async def streams(msg, mobj):
    """
    Retrieve the top Dota Two stream from Twitch.tv
    (Other Stream services need not apply)
    """
    return

@register_command
async def bulldog(msg, mobj):
    """
    Retrieve the latest video from Admiral Bulldog's YT
    """
    return

@register_command
async def sing_sing(msg, mobj):
    """
    Retrieve the latest video from SingSing
    Sing uploads a lot of videos so there's something to be had usually
    """
    return

@register_command
async def watafak(msg, mobj):
    """
    Retrieve the latest Dota Watafak video
    Brought to you buy GameLeap and G2A dot com
    """
    return

@register_command
async def fails(msg, mobj):
    """
    Retrieve the latest Fails video
    Realistically, DotaCinema does a lot more than just Fails
    """
    return

@register_command
async def wodota(msg, mobj):
    """
    Latest World of Dota video
    W E A R E E L E C T R I C
    """
    return

@register_command
async def purge(msg, mobj):
    """
    Yellow and this is the latest video from Purge
    """
    return

@register_command
async def slacks(msg, mobj):
    """
    From God himself, he brings to us thy glory
    """
    return

@register_command
async def divine(msg, mobj):
    """
    Dota 2 Divine memes R us
    """
    return

async def clarity(msg, mobj):
    """
    Dota 2 Clarity, a sane Dota 2 channel
    """
    return

@register_command
async def moonduck(msg, mobj):
    """
    The return of the duck
    """
    return

setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end
