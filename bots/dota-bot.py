#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Webhook automated Dota 2 match parsing service for Discord

"""

from json import load as jload, dump as jdump
from time import sleep
from botinfo import *
from requests import get, post
from pathlib import Path

DELAY_TIMER = 10 # 60 * 30
INBETWEEN_TIMER = 30

# Web hook key (this should be read from a keyfile)
WEB_HOOK = "https://discordapp.com/api/webhooks/296303788057427969/CUr6cezgCmIjYfVrbcxTIu2HnFKSorOUv15DKwnOoEvJcTFx8ZMNRR5RhQyNCqodHCHI"

OPENDOTA_API = "https://api.opendota.com/api"
OPENDOTA_URL = "https://opendota.com/matches"

filegen = create_filegen("shared")

HERO_DATA_PATH   = Path("shared/heroes.json")

# Load the cache (either from file or fresh JSON query)
if HERO_DATA_PATH.is_file():
    with open(HERO_DATA_PATH, "r") as f:
        HERO_DATA = jload(f)
else:
    r = get(f"{OPENDOTA_API}/heroes")
    if r.status_code != 200:
        logger(f"Failed to pre-fetch Hero JSON data from openDota")
        quit()
    HERO_DATA = r.json()
    with open(HERO_DATA_PATH, "w") as f:
        jdump(HERO_DATA, f)

SHARED = Path("shared")
logger = create_logger("dota-bot")

def get_payload(dota_id, match_id):
    """
    Craft a webhook payload
    """
    jsonblob = get(f"{OPENDOTA_API}/matches/{match_id}").json()
    print(jsonblob)
    data = dict()
    embs = []

    radiant_win = jsonblob["radiant_win"]
    radiant_score = jsonblob["radiant_score"]
    dire_score = jsonblob["dire_score"]
    game_mode = jsonblob["game_mode"]
    duration = jsonblob["duration"]

    minutes = str(duration // 60)
    seconds = str(duration % 60).zfill(2)

    player = None
    for p in jsonblob["players"]:
        if str(p["account_id"]) == dota_id:
            logger("Found the player")
            player = p
    if player is None:
        logger("Failed to find the player")
        return False

    # Player variable declarations for use later
    player_team = player["isRadiant"]
    pname = player["personaname"] 
    hero_name = "LOL"

    # Score of game
    embs.append({
        "name": "Final Score",
        "value": f"Radiant **{radiant_score}** - **{dire_score}** Dire",
        "inline": True
    })

    # Player Stats field
    if player_team:
        percent_of_team = round(((player["kills"]+player["assists"]) / float(radiant_score)) * 100.0, 2)
    else:
        percent_of_team = round(((player["kills"]+player["assists"]) / float(dire_score)) * 100.0, 2)
            
    embs.append({
        "name": "Stats (KDA)",
        "value": f"{player['kills']}/{player['deaths']}/{player['assists']} ({percent_of_team}% involvement)",
        "inline": True
    })

    # GPM / XPM
    embs.append({
        "name": "GPM / XPM",
        "value": f"{player['gold_per_min']} / {player['xp_per_min']}",
        "inline": True
    })

    # Replay sensitive data follows after this comment
    # OpenDota takes time to parse the replay of each match, such that more info can be gathered
    # from the match. Things like chat, pings, runes and damage instances are all based on replays
    # If this stuff isn't immediately available, it shouldn't be added to the Embed
    # ping details
    if 'pings' in player:
        total_pings = sum((p["pings"] for p in jsonblob["players"] if p["isRadiant"] == player_team))
        pingpc = round((float(player["pings"]) / total_pings) * 100.0, 2)
        embs.append({
            "name": "Total Pings",
            "value": f"{player['pings']} ({pingpc}% of team)",
            "inline": True
        })

    # rune details
    if 'runes' in player:
        pass


    # craft the main embed
    winstatus = "won" if player_team == radiant_win else "lost"
    data["embeds"] = [{
        "title": f"Results for Match #{match_id}",
        "description": f"{player['personaname']} {winstatus} as {hero_name} ({minutes}:{seconds})",
        "url": f"{OPENDOTA_URL}/{match_id}",
        "color": int(match_id % 0xffffff),
        "fields": embs,
        "footer": {
            "text": "Provided by OpenDota API"
        }
    }]
    return data

def fetch_last_match(path):
    dota_id = read_file(path)
    data = get(f"{OPENDOTA_API}/players/{dota_id}/matches?limit=1").json()
    if not data:
        return False # no matches played

    match_id = data[0]["match_id"]

    # Check the match_id versus the one in the cache
    # Check if a cache even exists
    cache = Path(f"{path}.cache")
    cache_v = 0
    if cache.is_file():
        with open(cache, 'r') as f:
            try:
                cache_v = int(f.read())
            except Exception:
                cache_v = 0
    else:
        with open(cache, 'w') as f:
            f.write(str(match_id))

    # Check if match_id is greater than cache_v
    if match_id <= cache_v:
        logger(f"{path}: Latest match not newer than cached match")
        return False
    
    payload = get_payload(dota_id, match_id)
    if not payload:
        logger("Failed to parse data for M#{match_id} (P#{dota_id})")
        return False
    res = post(WEB_HOOK, json=payload, headers={"content-type": "application/json"})
    return res

def main():
    logger("Beginning Match Parsing...")
    while True:
        keys = [f for f in SHARED.iterdir() if str(f).endswith("dota")]
        logger(f"Keys loaded: {len(keys)}")
        for f in keys:
            fetch_last_match(f)
            sleep(INBETWEEN_TIMER)
        sleep(DELAY_TIMER)
    logger("Exiting")

if __name__ == "__main__":
    main()
    pass
# end
