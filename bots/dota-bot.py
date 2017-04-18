#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Webhook automated Dota 2 match parsing service for Discord

"""

from json import load as jload, dump as jdump
from time import sleep
from random import choice
from pathlib import Path
from Bot import WebHookBot
from requests import get, post

class DotaBot(WebHookBot):
    """
    Automated match-fetching bot for Discord
    Users can register through a chat bot or the
    files can be stored on the host machine
    (or perhaps, even on a website?)
    """

    DELAY_GAP = 30
    OPENDOTA_API = "https://api.opendota.com/api"
    OPENDOTA_URL = "https://opendota.com/matches"
    HERO_FILE = "heroes.json" 
    
    def __init__(self, name):
        super(DotaBot, self).__init__(name)
        self.heroes     = list()
        self.filegen    = self._create_filegen("shared")
        self.herojson   = self.filegen(self.HERO_FILE)
        self.SLEEP_TIME = 60 * 60 # refresh every hour
        self._load_hero_data()

    def _load_hero_data(self, force=False):
        "Prefetch the Hero JSON from OpenDota"
        if self.herojson.is_file():
            with open(self.herojson, 'r') as f:
                self.heroes = jload(f)
                return
        r = get(f"{self.OPENDOTA_API}/heroes")
        if r.status_code != 200:
            raise IOError("Failed to prefetch Hero JSON data from OpenDota")
        with open(self.herojson, 'w') as f:
            jdump(r.json(), f)
        self.heroes = r.json()
        return

    def find_hero(self, hid):
        "Wrapper for finding a hero in a haystack of heroes"
        for hero in self.heroes:
            if hero["id"] == hid:
                return hero["localized_name"]
        return "Jebaited"

    @staticmethod
    def to_percent(a=0, b=0, d=1):
        "Convert (a+b)/d to a 1.23 float"
        if d == 0:
            raise ZeroDivisionError("Can't do that")
        return round(((a+b)/float(d))*100.0 , 2)

    @staticmethod
    def get_timestr(seconds_i):
        # divide the seconds into minutes, then 
        minutes = seconds_i // 60
        seconds = f"{seconds_i % 60}".zfill(2)
        hours = ""
        if minutes > 59:
            hours = f"{minutes // 60}:"
            minutes = f"{minutes % 60}".zfill(2)
        return f"{hours}{minutes}:{seconds}"

    @staticmethod
    def get_score(p, team, rad_i, dir_i):
        "Create a player statistical score string"
        if team:
            return DotaBot.to_percent(p['kills'], p['assists'], rad_i)
        return DotaBot.to_percent(p['kills'], p['assists'], dir_i)

    def get_last_match(self, player_path):
        """
        Get the last match from a given file
        Yield a pair of strings (Match ID * Dota ID) when the match
        differs from the cache
        If not newer, return (None * None)
        """
        if not player_path.is_file():
            raise IOError("Invalid Path() given for get_last_match()")
        dota_id = player_path.read_text().strip("\n") 

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
            cache_v = int(cache.read_text()) # bad

        # If the cache value is different from the new match iD,
        # Write to the cache file and return the (Match * ID) pair
        if cache_v != match_id:
            cache.write_text(str(match_id))
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
        
        # Game dependent variables
        radiant_win   = jsonblob["radiant_win"]
        radiant_score = jsonblob["radiant_score"]
        dire_score    = jsonblob["dire_score"]
        game_mode     = jsonblob["game_mode"]
        duration      = self.get_timestr(jsonblob["duration"])
        
        player = None
        for p in jsonblob["players"]:
            if str(p["account_id"]) == dota_id:
                player = p
        if player is None:
            self.logger("Failed to find the player")
            return None 
                
        # Player variable declarations for use later
        player_team = player["isRadiant"]
        pname = player["personaname"]
        hero_name = self.find_hero(player["hero_id"])
        
        # Score of game
        embs.append({
            "name": "Final Score",
            "value": f"Radiant **{radiant_score}** - **{dire_score}** Dire",
            "inline": True
        })
    
        # Player Stats field
        perc_team = self.get_score(player, radiant_win, radiant_score, dire_score)
        
        embs.append({
            "name": "Stats (KDA)",
            "value": f"{player['kills']}/{player['deaths']}/{player['assists']} ({perc_team}% involvement)",
            "inline": True
        })
        
        # GPM / XPM
        embs.append({
            "name": "GPM / XPM",
            "value": f"{player['gold_per_min']} / {player['xp_per_min']}",
            "inline": True
        })

        # Damge / Healing / Towers
        embs.append({
            "name": "HD / HH / TD",
            "value": f"{player['hero_damage']} / {player['hero_healing']} / {player['tower_damage']}",
            "inline": True,
        })
        
        # replay sensitive data is still tagged in the JSON output
        # such that trying to access a replay tag will always be None
        # ping details
        pings = player.get('pings', None)
        if pings is not None:
            total_pings = sum([p.get('pings', 0) for p in jsonblob["players"] if p["isRadiant"] == player_team])
            pingpc = self.to_percent(pings, 0, total_pings)
            embs.append({
                "name": "Total Pings",
                "value": f"{player['pings']} ({pingpc}% of team)",
                "inline": True
            })

        # rune details - fetch the bounty rune stuff
        runes = player.get('runes', None)
        if runes is not None:
            total_bounties = sum([p['runes']['5'] for p in jsonblob['players']])
            bountypc = self.to_percent(runes['5'], 0, total_bounties)
            embs.append({
                "name": "Bounties Collected",
                "value": f"{runes['5']} ({bountypc}% of game)",
                "inline": True
            })

        # Fetch a random quote from the match
        chat = jsonblob.get('chat', None)
        if 'chat' is not None:
            user_lines = [l['key'] for l in chat if l['unit'] == pname]
            if user_lines:
                embs.append({
                    "name": "Random Quote",
                    "value": f"'{choice(user_lines)}' -{pname}",
                    "inline": True
                })
        
        # craft the main embed
        winstatus = "won" if player_team & radiant_win else "lost"
        data["embeds"] = [{
            "title": f"Results for Match #{match_id}",
            "description": f"{player['personaname']} {winstatus} as {hero_name} ({duration})",
            "url": f"{self.OPENDOTA_URL}/{match_id}",
            "color": match_id % 0xffffff,
            "fields": embs,
            "footer": {
                "text": "Provided by OpenDota API"
            }
        }]
        return data

    def post_payload(self, data={}):
        "Send a data dict to the Discord endpoint"
        if not data:
            return False
        re = post(self.endpoint, json=data, headers={'content-type': 'application/json'})
        return re

    def main(self):
        self.logger(f"Heroes loaded: {len(self.heroes)}")
        files = [f for f in self.filegen().iterdir() if f"{f}".endswith("dota")]
        self.logger(f"Keys: {files}")
        for keypath in files:
            last_match, dota_id = self.get_last_match(keypath)
            if last_match is not None:
                self.logger("Posting match")
                payload = self.get_payload(last_match, dota_id)
                if not payload: 
                    self.logger("Failed to craft a payload")
                r = self.post_payload(payload)
            sleep(self.DELAY_GAP)
            pass

if __name__ == "__main__":
    bot = DotaBot("dota-bot")
    bot.run()
# end
