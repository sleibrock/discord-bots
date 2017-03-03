#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Dota bot

This bot's goal is aimed at Dota-related activities
"""

from random import choice
from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from json import load as jload
from pathlib import Path

# build a static list of heroes/items here
# Instead of waiting on a net request, just write them all
# Include whether a hero is RANGED, MELEE, or MIXED
# This will determine rules for melee/ranged bonus items
HEROES = [
    {"name": "Abaddon",             "type": "melee"},
    {"name": "Alchemist",           "type": "melee"},
    {"name": "Ancient Apparition",  "type": "ranged"},
    {"name": "Anti-Mage",           "type": "melee"},
    {"name": "Arc Warden",          "type": "ranged"},
    {"name": "Axe",                 "type": "melee"},
    {"name": "Bane",                "type": "ranged"},
    {"name": "Batrider",            "type": "ranged"},
    {"name": "Beastmaster",         "type": "melee"},
    {"name": "Bloodseeker",         "type": "melee"},
    {"name": "Bounty Hunter",       "type": "melee"},
    {"name": "Brewmaster",          "type": "melee"},
    {"name": "Bristleback",         "type": "melee"},
    {"name": "Broodmother",         "type": "melee"},
    {"name": "Centaur Warrunner",   "type": "melee"},
    {"name": "Chaos Knight",        "type": "melee"},
    {"name": "Chen",                "type": "ranged"},
    {"name": "Clinkz",              "type": "ranged"},
    {"name": "Clockwerk",           "type": "melee"},
    {"name": "Crystal Maiden",      "type": "melee"},
    {"name": "Dark Seer",           "type": "melee"},
    {"name": "Dazzle",              "type": "ranged"},
    {"name": "Death Prophet",       "type": "ranged"},
    {"name": "Disruptor",           "type": "ranged"},
    {"name": "Doom",                "type": "melee"},
    {"name": "Dragon Knight",       "type": "mixed"},
    {"name": "Drow Ranger",         "type": "ranged"},
    {"name": "Earth Spirit",        "type": "melee"},
    {"name": "Earthshaker",         "type": "melee"},
    {"name": "Elder Titan",         "type": "melee"},
    {"name": "Ember Spirit",        "type": "melee"},
    {"name": "Enchantress",         "type": "ranged"},
    {"name": "Enigma",              "type": "ranged"},
    {"name": "Faceless Void",       "type": "melee"},
    {"name": "Gyrocopter",          "type": "ranged"},
    {"name": "Huskar",              "type": "ranged"},
    {"name": "Invoker",             "type": "ranged"},
    {"name": "Io",                  "type": "ranged"},
    {"name": "Jakiro",              "type": "ranged"},
    {"name": "Juggernaut",          "type": "melee"},
    {"name": "Keeper of the Light", "type": "ranged"},
    {"name": "Kunkka",              "type": "melee"},
    {"name": "Legion Commander",    "type": "melee"},
    {"name": "Leshrac",             "type": "ranged"},
    {"name": "Lich",                "type": "ranged"},
    {"name": "Lifestealer",         "type": "melee"},
    {"name": "Lina",                "type": "ranged"},
    {"name": "Lion",                "type": "ranged"},
    {"name": "Lone Druid",          "type": "mixed"},
    {"name": "Luna",                "type": "ranged"},
    {"name": "Lycan",               "type": "melee"},
    {"name": "Magnus",              "type": "melee"},
    {"name": "Medusa",              "type": "ranged"},
    {"name": "Meepo",               "type": "melee"},
    {"name": "Mirana",              "type": "ranged"},
    {"name": "Monkey King",         "type": "melee"},
    {"name": "Morphling",           "type": "ranged"},
    {"name": "Naga Siren",          "type": "melee"},
    {"name": "Nature's Prophet",    "type": "melee"},
    {"name": "Necrophos",           "type": "ranged"},
    {"name": "Nightstalker",        "type": "melee"},
    {"name": "Nyx Assassin",        "type": "melee"},
    {"name": "Ogre Magi",           "type": "melee"},
    {"name": "Omniknight",          "type": "melee"},
    {"name": "Oracle",              "type": "ranged"},
    {"name": "Outworld Devourer",   "type": "ranged"},
    {"name": "Phantom Assassin",    "type": "melee"},
    {"name": "Phantom Lancer",      "type": "melee"},
    {"name": "Phoenix",             "type": "ranged"},
    {"name": "Puck",                "type": "ranged"},
    {"name": "Pudge",               "type": "melee"},
    {"name": "Pugna",               "type": "ranged"},
    {"name": "Queen of Pain",       "type": "ranged"},
    {"name": "Razor",               "type": "ranged"},
    {"name": "Riki",                "type": "melee"},
    {"name": "Rubick",              "type": "ranged"},
    {"name": "Sand King",           "type": "melee"},
    {"name": "Shadow Demon",        "type": "ranged"},
    {"name": "Shadow Fiend",        "type": "ranged"},
    {"name": "Shadow Shaman",       "type": "ranged"},
    {"name": "Silencer",            "type": "ranged"},
    {"name": "Skywrath Mage",       "type": "ranged"},
    {"name": "Slardar",             "type": "melee"},
    {"name": "Slark",               "type": "melee"},
    {"name": "Sniper",              "type": "ranged"},
    {"name": "Spectre",             "type": "melee"},
    {"name": "Spirit Breaker",      "type": "melee"},
    {"name": "Storm Spirit",        "type": "ranged"},
    {"name": "Sven",                "type": "melee"},
    {"name": "Techies",             "type": "ranged"},
    {"name": "Templar Assassin",    "type": "ranged"},
    {"name": "Terrorblade",         "type": "mixed"},
    {"name": "Tidehunter",          "type": "melee"},
    {"name": "Timbersaw",           "type": "melee"},
    {"name": "Tinker",              "type": "ranged"},
    {"name": "Tiny",                "type": "melee"},
    {"name": "Treant Protector",    "type": "melee"},
    {"name": "Troll Warlord",       "type": "mixed"},
    {"name": "Tusk",                "type": "melee"},
    {"name": "Underlord",           "type": "melee"},
    {"name": "Undying",             "type": "melee"},
    {"name": "Ursa",                "type": "melee"},
    {"name": "Vengeful Spirit",     "type": "ranged"},
    {"name": "Venomancer",          "type": "ranged"},
    {"name": "Viper",               "type": "ranged"},
    {"name": "Visage",              "type": "ranged"},
    {"name": "Warlock",             "type": "ranged"},
    {"name": "Weaver",              "type": "ranged"},
    {"name": "Windranger",          "type": "ranged"},
    {"name": "Winter Wyvern",       "type": "ranged"},
    {"name": "Wraith King",         "type": "melee"},
    {"name": "Zeus",                "type": "ranged"},
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
    {"name": "Guardian Greaves", "price": 5250},
]

# Optional tie-ins for certain types of characters
MELEE_ONLY = [
    {"name": "Echo Saber", "price": 2650},
]

RANGED_ONLY = [
    {"name": "Dragon Lance", "price": 1900},
]

# Rapier won't be included as it can lead to many game losses
# Each item has an associated cost so you can measure how much
# gold is required to reach your target (and possibly re-roll
# if the GPM is just an impossibility for your given character)
ITEMS = [
    {"name": "Daedelus",                  "price": 5520},
    {"name": "Abyssal Blade",             "price": 6400},
    {"name": "Monkey King Bar",           "price": 5400},
    {"name": "Eye of Skadi",              "price": 5675},
    {"name": "Bloodthorn",                "price": 7195},
    {"name": "Radiance",                  "price": 5150},
    {"name": "Manta Style",               "price": 4950},
    {"name": "Battlefury",                "price": 4500},
    {"name": "Silver Edge",               "price": 5100},
    {"name": "Helm of the Dominator",     "price": 1800},
    {"name": "Mask of Madness",           "price": 1900},
    {"name": "Diffusal Blade",            "price": 3150},
    {"name": "Sange and Yasha",           "price": 4100},
    {"name": "Mjollnir",                  "price": 5700},
    {"name": "Butterfly",                 "price": 5525},
    {"name": "Blink Dagger",              "price": 2250},
    {"name": "Moon Shard",                "price": 4000},
    {"name": "Desolator",                 "price": 3500},
    {"name": "Satanic",                   "price": 5800},
    {"name": "Heaven's Halberd",          "price": 3500},
    {"name": "Blaemail",                  "price": 2200},
    {"name": "Crimson Guard",             "price": 3550},
    {"name": "Assault Cuirass",           "price": 5250},
    {"name": "Black King Bar",            "price": 3975},
    {"name": "Shiva's Guard",             "price": 4700},
    {"name": "Lotus Orb",                 "price": 4000},
    {"name": "Linken's Sphere",           "price": 4800},
    {"name": "Heart of Tarrasque",        "price": 5500},
    {"name": "Ethereal Blade",            "price": 4700},
    {"name": "Dagon",                     "price": 2720},
    {"name": "Necronomicon",              "price": 2650},
    {"name": "Rod of Atos",               "price": 3100},
    {"name": "Eul's Scepter of Divinity", "price": 2750},
    {"name": "Veil of Discord",           "price": 2240},
    {"name": "Aghanim's Scepter",         "price": 4200},
    {"name": "Bloodstone",                "price": 4900},
    {"name": "Refresher Orb",             "price": 5200},
    {"name": "Glimmer Cape",              "price": 1850},
    {"name": "Aether Lens",               "price": 2350},
    {"name": "Force Staff",               "price": 2250},
    {"name": "Pipe of Insight",           "price": 3100},
    {"name": "Solar Crest",               "price": 2625},
    {"name": "Vladmir's Offering",        "price": 2275},
]

bot_name = "dota-bot"
client   = discord.Client()
logger   = create_logger(bot_name)
bot_data = create_filegen(bot_name)

# API endpoints go here
OPENDOTA_URL = "https://opendota.com/matches"
OPENDOTA_API = "https://api.opendota.com/api"

# Prefetch a list of heroes from OpenDota
# Cache it to disk just to avoid making too many reqs
hero_dataf = Path(bot_data("heroes.json"))
if not hero_dataf.is_file():
    r = re_get(f"{OPENDOTA_API}/heroes")
    if r.status_code != 200:
        print(f"Error pre-fetching hero data (code: {r.status_code})")
    with open(hero_dataf, "w") as f:
        f.write(r.json())

hero_data = jload(hero_dataf)

@register_command
async def osfrog(msg, mobj):
    """
    Patch 7.02: help string was removed from Captain's Mode 
    """
    osfrogs = [
        "Added Monkey King to the game",
        "Reduced Lone Druid's respawn talent -50s to -40s",
    ]
    return await client.send_message(mobj.channel, choice(osfrogs))

@register_command
async def challenge(msg, mobj):
    """
    The Challenge
    Picks a random Dota 2 hero to play and gives you 3 items to work towards
    Optional: supply a hero and get the 3 items to play (sd/ap/rd applicable)
    Example: !challenge
             -> Bloodseeker: Guardian Greaves, Abyssal Blade, Dagon 
    """
    msg = []
    hs = msg.strip().lower().capitalize()
    if hs != "":
        search = [h for h in HEROES if h["name"] == hs]
        if not search:
            return await client.send_message(mobj.channel, "Couldn't find hero")
        hero = search[0]
    else:
        hero = choice(HEROES)
        msg.append(f"Hero: {hero['name']}")

    item_pool = ITEMS
    if hero["type"] == "mixed":
        item_pool.extend(MELEE_ONLY)
        item_pool.extend(RANGED_ONLY)
    elif hero["type"] == "melee":
        item_pool.extend(MELEE_ONLY)
    else:
        item_pool.extend(RANGED_ONLY)
    shuffle(item_pool)

    # Start filling the pool with items
    boots = choice(BOOTS)
    picked_items = []
    while len(picked_items) < 3:
        picked_items.append(item_pool.pop(0))
        shuffle(item_pool)

    msg.append(f"Hero: {hero['name']}")
    msg.append(f"Items: {', '.join([i['name'] for i in picked_items])}")
    msg.append(f"Total cost: {sum([i['price'] for i in picked_items])}")
    
    return await client.send_message(mobj.channel, "\n".join(msg))

@register_command
async def dota_id(msg, mobj):
    """
    Register's a user's Discord ID and associates it with a Dota ID
    This is used to retrieve a user's last played match from OpenDota 
    The string must be tested against OpenDota's API to see if it's valid
    """
    if len(msg) > 30:
        return await client.send_message(mobj.channel, "Bro that's too long")

    r = re_get(f"{OPENDOTA_API}/players/{msg.strip()}")
    if r.status_code != 200:
        return await client.send_message(mobj.channel, "Invalid Dota ID")

    fname = bot_data(f"{mobj.author.id}.txt")
    print(fname)
    with open(fname, 'w') as f:
        f.write(msg.strip())

    print("Returning")
    return await client.send_message(mobj.channel, "Registered your Dota ID")

@register_command
async def lastmatch(msg, mobj):
    """
    Fetch a user's ID from the FS and yield the last played match
    from the OpenDota API
    The user must first associate a Dota ID with !dota_id to use this
    """
    fname = bot_data(f"{mobj.author.id}.txt") 
    dota_id = None
    with open(fname, 'r') as f:
        dota_id = f.read().strip("\n")

    r    = re_get(f"{OPENDOTA_API}/players/{dota_id}/matches?limit=1") 
    if r.status_code != 200:
        return await client.send_message(mobj.channel, "Failed to get matches")

    data = r.json()
    mid  = data[0]['match_id']
    mr   = re_get(f"{OPENDOTA_API}/matches/{mid}")
    if mr.status_code != 200:
        return await client.send_message(mobj.channel, "Error retrieving data")

    # Find the player object in the players property
    mdata   = mr.json()
    players = mdata["players"]
    pfilter = [p for p in players if p["account_id"] == dota_id]
    if not user:
        return await client.send_message(mobj.channel, f"Couldn't find user (???)")
    player  = pfilter[0]
    victory = "won" if player["win"] == 1 else "lost"

    # Start grabbing details
    pname        = player["personaname"]
    heroid       = player["heroid"]
    kills        = player["kills"]
    deaths       = player["deaths"]
    assists      = player["assists"]
    gpm          = player["gold_per_min"]
    damage_dealt = player["hero_damage"]
    team         = player["isRadiant"] # t if Rad, f if Dire
    kda          = float(kills+assists) / deaths

    # Grab Ping details of entire team
    ppings      = player["pings"]
    total_pings = sum([p["pings"] for p in players if p["isRadiant"] == team])
    pingpc      = float(ppings) / total_pings

    # Grab bounty runes picked up (bounty is ID# 5)
    bounties = player["runes"].get(5, 0)
    all_bounties = sum([p["runes"].get(5, 0) for p in players])
    bcp = float(bounties) / all_bounties

    # Grab messages sent in all chat
    allchat = mdata["chat"]
    allchat_count = len([m for m in allchat if m["unit"] = pname])
    acp = (float(allchat_count) / len(allchat)) * 100.0

    # Get team's kills and calculate kill participation
    ts = mdata["radiant_score"] if team else mdata["dire_score"]
    kp = float(kills+assists) / ts

    lines = []
    lines.append(f"{pname} {victory} as {hero_name}")
    lines.append(f"Score: {kills}/{deaths}/{assists}  KDA: {kda}  GPM: {gpm}")
    lines.append(f"Total damage dealt: {damage_dealt}")

    if bounties:
        lines.append(f"Bounty runes picked: {bounties} ({bcp}% of all bounties)")

    if allchat_count: 
        lines.append(f"Allchat count: {allchat_count} ({acp}% of allchat)")

    if ppings:
        lines.append(f"Pings spammed: {ppings} ({pingpc}% of team)")
    
    return await client.send_message(mobj.channel, f"{OPENDOTA_URL}/{mid}")

@register_command
def last100(msg, mobj):
    """
    Report winrate stats in the last 100 matches
    """
    pass

setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end
