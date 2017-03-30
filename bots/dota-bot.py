#!/usr/bin/env python
#-*- coding: utf-8 -*-

from json import load as jload, dump as jdump
from time import sleep
from botinfo import *
from requests import get, post
from pathlib import Path

DELAY_TIMER = 10 # 60 * 30
INBETWEEN_TIMER = 30

WEB_HOOK = "https://discordapp.com/api/webhooks/296303788057427969/CUr6cezgCmIjYfVrbcxTIu2HnFKSorOUv15DKwnOoEvJcTFx8ZMNRR5RhQyNCqodHCHI"

OPENDOTA_API = "https://api.opendota.com/api"
OPENDOTA_URL = "https://opendota.com/matches"

HERO_DATA_CACHED = False
HERO_DATA_PATH   = Path("shared/heroes.json")

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

    player = None
    for p in jsonblob["players"]:
        if str(p["account_id"]) == dota_id:
            logger("Found the player")
            player = p
    if player is None:
        logger("Failed to find the player")
        return False

    # Score field
    embs.append({
        "name": "Score (KDA)",
        "value": f"{player['kills']}/{player['deaths']}/{player['assists']}",
        "inline": True
    })

    # craft the main embed
    data["embeds"] = [{
        "title": f"Results for Match #{match_id}",
        "description": "something something player victory status",
        "url": f"{OPENDOTA_URL}/{match_id}",
        #"color": int(match_id % 0xffffff),
        #"fields": embs,
        #"footer": {
        #    "text": "Provided by OpenDota API"
        #}
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

    """
    Test this blob
    
    {"embeds":[{"title":"Results for Match 3086034297","description":"Ste5e lost as Bristleback","url":"https://opendota.com/matches/3086034297","color":15803952,"footer":{"url":"http://cdn.dota2.com/apps/dota2/images/nav/logo.png","width":167,"height":33},"fields":[{"name":"K/D/A","value":"4/6/11","inline":true},{"name":"GPM / XPM","value":"418 / 645","inline":true},{"name":"Pings Used","value":"55 (49.11% of team)","inline":true},{"name":"Bounty Runes Collected","value":"6 (9.23% of all bounties)","inline":true},{"name":"Longest Chat","value":"'these 2 are fuckin kiddin me' -Ste5e","inline":true}]}]}
    """
    
    print(data)
    payload = get_payload(dota_id, match_id)
    print(payload)
    res = post(WEB_HOOK, payload)
    print(res)
    post(WEB_HOOK, {"embeds": [{"title":"Test","description": "test description", "url":"https://google.com/","color":200, "fields":[{"name":"test","value":"test message", "inline":True}]}]})
    post(WEB_HOOK, {"content": "test"})
    return

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
