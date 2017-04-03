#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Webhook automated Dota 2 match parsing service for Discord

"""

from json import load as jload, dump as jdump
from time import sleep
from pathlib import Path
from Bot import WebHookBot
from requests import get, post

class Dotabot(WebHookBot):

    DELAY_GAP = 30
    OPENDOTA_API = "https://api.opendota.com/api"
    OPENDOTA_URL = "https://opendota.com/matches"
    HERO_FILE = "heroes.json" 
    
    def __init__(self, name):
        super(Dotabot, self).__init__(name)
        self.SLEEP_TIME = 60 * 20
        self.filegen = self._create_filegen("shared")
        self.heroes = list()
        self.herojson = self.filegen(self.HERO_FILE)

    def _load_hero_data(self):
        if self.herojson.is_file():
            with open(self.herojson, 'r') as f:
                self.heroes = jload(f)
        else:
            r = get(f"{self.OPENDOTA_API}/heroes")
            if r.status_code != 200:
                raise IOError("Failed to prefetch Hero JSON data from OpenDota")
            with open(self.herojson, 'w') as f:
                jdump(r.json(), f)
            self.heroes = r.json()
        return

    def get_last_match(self, player_path):
        """
        Get the last match from a given file
        Yield a pair of strings (Match ID * Dota ID) when the match
        differs from the cache
        If not newer, return (None * None)
        """
        dota_id = None
        if not player_path.is_file():
            raise IOError("Invalid Path() given for get_last_match()")
        with open(player_path, 'r') as f:
            dota_id = f.read().strip("\n")

        resp = get(f"{self.OPENDOTA_API}/players/{dota_id}/matches?limit=1")
        if resp.status_code != 200:
            self.logger(f"Couldn't load matches for {dota_id}")
            return (None, None)

        data = resp.json()
        if not data:
            return (None, None) # no matches played
        
        match_id = data[0]["match_id"]
        
        # Check the match_id versus the one in the cache
        # Check if a cache even exists
        cache = Path(f"{player_path}.cache")
        cache_v = 0
        if cache.is_file():
            with open(cache, 'r') as f:
                    cache_v = int(f.read())

        # If the cache value is different from the new match iD,
        # Write to the cache file and return the (Match * ID) pair
        if cache_v != match_id:
            with open(cache, 'w') as f:
                f.write(str(match_id))
            return (match_id, dota_id)
        return (None, None)
                
    def get_payload(self, match_id, dota_id):
        """
        Craft a payload of Dota 2 match info
        The nested JSON is per the Discord webhook Embed format
        
        TODO: think of a sane way to compose these into functions perhaps?
        """
        resp = get(f"{self.OPENDOTA_API}/matches/{match_id}")
        if resp.status_code != 200:
            raise IOError("Failed to get data from OpenDota API")
        jsonblob = resp.json()
        data = dict()
        embs = list()
                    
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
                self.logger("Found the player")
                player = p
        if player is None:
            self.logger("Failed to find the player")
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
            "url": f"{self.OPENDOTA_URL}/{match_id}",
            "color": int(match_id % 0xffffff),
            "fields": embs,
            "footer": {
                "text": "Provided by OpenDota API"
            }
        }]
        return data

    def post_payload(self, data={}):
        """
        Send a dictionary of data to the Discord endpoint
        """
        if not data:
            return False
        re = post(self.endpoint, json=data, headers={'content-type': 'application/json'})
        return re

    def main(self):
        self._load_hero_data()
        self.logger(f"Heroes loaded: {len(self.heroes)}")
        files = [f for f in self.filegen().iterdir() if f"{f}".endswith("dota")]
        self.logger(f"Keys: {files}")
        for keypath in files:
            last_match, dota_id = self.get_last_match(keypath)
            if last_match is not None:
                print("Posting match")
                payload = self.get_payload(last_match, dota_id)
                if not payload: 
                    self.logger("Failed to craft a payload")
                r = self.post_payload(payload)
                print(r.status_code)
            sleep(self.DELAY_GAP)
            pass

if __name__ == "__main__":
    bot = Dotabot("dotabot")
    bot.run()
# end
