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
# Include whether a hero is RANGED, MELEE, or MIXED
# This will determine rules for melee/ranged bonus items
HEROES = [
    {"name": "Abaddon", "type": "melee"},
    {"name": "Alchemist", "type": "melee"},
    {"name": "Ancient Apparition", "type": "ranged"},
    {"name": "Anti-Mage", "type": "melee"},
    {"name": "Arc Warden", "type": "ranged"},
    {"name": "Axe", "type": "melee"},
    {"name": "Bane", "type": "ranged"},
    {"name": "Batrider", "type": "ranged"},
    {"name": "Beastmaster", "type": "melee"},
    {"name": "Bloodseeker", "type": "melee"},
    {"name": "Bounty Hunter", "type": "melee"},
    {"name": "Brewmaster", "type": "melee"},
    {"name": "Bristleback", "type": "melee"},
    {"name": "Broodmother", "type": "melee"},
    {"name": "Centaur Warrunner", "type": "melee"},
    {"name": "Chaos Knight", "type": "melee"},
    {"name": "Chen", "type": "ranged"},
    {"name": "Clinkz", "type": "ranged"},
    {"name": "Clockwerk", "type": "melee"},
    {"name": "Crystal Maiden", "type": "melee"},
    {"name": "Dark Seer", "type": "melee"},
    {"name": "Dazzle", "type": "ranged"},
    {"name": "Death Prophet", "type": "ranged"},
    {"name": "Disruptor", "type": "ranged"},
    {"name": "Doom", "type": "melee"},
    {"name": "Dragon Knight", "type": "mixed"},
    {"name": "Drow Ranger", "type": "ranged"},
    {"name": "Earth Spirit", "type": "melee"},
    {"name": "Earthshaker", "type": "melee"},
    {"name": "Elder Titan", "type": "melee"},
    {"name": "Ember Spirit", "type": "melee"},
    {"name": "Enchantress", "type": "ranged"},
    {"name": "Enigma", "type": "ranged"},
    {"name": "Faceless Void", "type": "melee"},
    {"name": "Gyrocopter", "type": "ranged"},
    {"name": "Huskar", "type": "ranged"},
    {"name": "Invoker", "type": "ranged"},
    {"name": "Io", "type": "ranged"},
    {"name": "Jakiro", "type": "ranged"},
    {"name": "Juggernaut", "type": "melee"},
    {"name": "Keeper of the Light", "type": "ranged"},
    {"name": "Kunkka", "type": "melee"},
    {"name": "Legion Commander", "type": "melee"},
    {"name": "Leshrac", "type": "ranged"},
    {"name": "Lich", "type": "ranged"},
    {"name": "Lifestealer", "type": "melee"},
    {"name": "Lina", "type": "ranged"},
    {"name": "Lion", "type": "ranged"},
    {"name": "Lone Druid", "type": "mixed"},
    {"name": "Luna", "type": "ranged"},
    {"name": "Lycan", "type": "melee"},
    {"name": "Magnus", "type": "melee"},
    {"name": "Medusa", "type": "ranged"},
    {"name": "Meepo", "type": "melee"},
    {"name": "Mirana", "type": "ranged"},
    {"name": "Monkey King", "type": "melee"},
    {"name": "Morphling", "type": "ranged"},
    {"name": "Naga Siren", "type": "melee"},
    {"name": "Nature's Prophet", "type": "melee"},
    {"name": "Necrophos", "type": "ranged"},
    {"name": "Nightstalker", "type": "melee"},
    {"name": "Nyx Assassin", "type": "melee"},
    {"name": "Ogre Magi", "type": "melee"},
    {"name": "Omniknight", "type": "melee"},
    {"name": "Oracle", "type": "ranged"},
    {"name": "Outworld Devourer", "type": "ranged"},
    {"name": "Phantom Assassin", "type": "melee"},
    {"name": "Phantom Lancer", "type": "melee"},
    {"name": "Phoenix", "type": "ranged"},
    {"name": "Puck", "type": "ranged"},
    {"name": "Pudge", "type": "melee"},
    {"name": "Pugna", "type": "ranged"},
    {"name": "Queen of Pain", "type": "ranged"},
    {"name": "Razor", "type": "ranged"},
    {"name": "Riki", "type": "melee"},
    {"name": "Rubick", "type": "ranged"},
    {"name": "Sand King", "type": "melee"},
    {"name": "Shadow Demon", "type": "ranged"},
    {"name": "Shadow Fiend", "type": "ranged"},
    {"name": "Shadow Shaman", "type": "ranged"},
    {"name": "Silencer", "type": "ranged"},
    {"name": "Skywrath Mage", "type": "ranged"},
    {"name": "Slardar", "type": "melee"},
    {"name": "Slark", "type": "melee"},
    {"name": "Sniper", "type": "ranged"},
    {"name": "Spectre", "type": "melee"},
    {"name": "Spirit Breaker", "type": "melee"},
    {"name": "Storm Spirit", "type": "ranged"},
    {"name": "Sven", "type": "melee"},
    {"name": "Techies", "type": "ranged"},
    {"name": "Templar Assassin", "type": "ranged"},
    {"name": "Terrorblade", "type": "mixed"},
    {"name": "Tidehunter", "type": "melee"},
    {"name": "Timbersaw", "type": "melee"},
    {"name": "Tinker", "type": "ranged"},
    {"name": "Tiny", "type": "melee"},
    {"name": "Treant Protector", "type": "melee"},
    {"name": "Troll Warlord", "type": "mixed"},
    {"name": "Tusk", "type": "melee"},
    {"name": "Underlord", "type": "melee"},
    {"name": "Undying", "type": "melee"},
    {"name": "Ursa", "type": "melee"},
    {"name": "Vengeful Spirit", "type": "ranged"},
    {"name": "Venomancer", "type": "ranged"},
    {"name": "Viper", "type": "ranged"},
    {"name": "Visage", "type": "ranged"},
    {"name": "Warlock", "type": "ranged"},
    {"name": "Weaver", "type": "ranged"},
    {"name": "Windranger", "type": "ranged"},
    {"name": "Winter Wyvern", "type": "mixed"},
    {"name": "Wraith King", "type": "melee"},
    {"name": "Zeus", "type": "ranged"},
]

# Boots to pick from
# Guardian Greaves is ignored because that's more of a flex pickup
# It won't even qualify for normal items just because of it's nature
BOOTS = [
    {"name": "Phase Boots", "price": 1240},
    {"name": "Tranquil Boots", "price": 900},
    {"name": "Power Treads", "price": 1350},
    {"name": "Boots of Travel", "price": 2400},
    {"name": "Arcane Boots", "price": 1300},
]

# Optional tie-ins for certain types of characters
MELEE_ONLY = [
    {"name": "Echo Saber", "price": 2650},
]

RANGED_ONLY = [
    {"name": "Hurricane Pike", "price": 4375},
]

# Rapier won't be included as it can lead to many game losses
# Each item has an associated cost so you can measure how much
# gold is required to reach your target (and possibly re-roll
# if the GPM is just an impossibility for your given character)
ITEMS = [
    {"name": "Daedelus", "price": 5520},
    {"name": "Abyssal Blade", "price": 6400},
    {"name": "Monkey King Bar", "price": 5400},
    {"name": "Eye of Skadi", "price": 5675},
    {"name": "Bloodthorn", "price": 7195},
    {"name": "Radiance", "price": 5150},
    {"name": "Manta Style", "price": 4950},
    {"name": "Battlefury", "price": 4500},
    {"name": "Silver Edge", "price": 5100},
    {"name": "Helm of the Dominator", "price": 1800},
    {"name": "Mask of Madness", "price": 1900},
    {"name": "Diffusal Blade", "price": 3150},
    {"name": "Sange and Yasha", "price": 4100},
    {"name": "Mjollnir", "price": 5700},
    {"name": "Butterfly", "price": 5525},
    {"name": "Blink Dagger", "price": 2250},
    {"name": "Moon Shard", "price": 4000},
    {"name": "Desolator", "price": 3500},
    {"name": "Satanic", "price": 5800},
    {"name": "Heaven's Halberd", "price": 3500},
    {"name": "Blaemail", "price": 2200},
    {"name": "Crimson Guard", "price": 3550},
    {"name": "Black King Bar", "price": 3975},
    {"name": "Shiva's Guard", "price": 4700},
    {"name": "Lotus Orb", "price": 4000},
    {"name": "Linken's Sphere", "price": 4800},
    {"name": "Heart of Tarrasque", "price": 5500},
    {"name": "Ethereal Blade", "price": 4700},
    {"name": "Dagon", "price": 2720}, # do the calculation later
    {"name": "Necronomicon", "price": 2650},
    {"name": "Rod of Atos", "price": 3100},
    {"name": "Eul's Scepter of Divinity", "price": 2750},
    {"name": "Veil of Discord", "price": 2240},
    {"name": "Aghanim's Scepter", "price": 4200},
    {"name": "Bloodstone", "price": 4900},
    {"name": "Refresher Orb", "price": 5200},
    {"name": "Glimmer Cape","price": 1850},
    {"name": "Aether Lens","price": 2350},
    {"name": "Pipe of Insight","price": 3100},
    {"name": "Solar Crest","price": 2625},
    {"name": "Vladmir's Offering","price": 2275},
]

bot_name = "dota-bot"
client = discord.Client()
logger = create_logger(bot_name)

# API endpoints go here
TWITCH_API = ""
OPENDOTA_API = ""
YOUTUBE_URL = ""

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
    return await client.send_message(mobj.channel, ":frog:")

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

# All youtube scrapes below
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
