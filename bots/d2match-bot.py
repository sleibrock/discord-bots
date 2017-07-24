#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Webhook automated Dota 2 match parsing service for Discord

Users can register their IDs via a chatbot and the Dota bot
will look for local JSON files in the botdata/shared folder.
JSON files are where Dota player IDs are stored, as well as
the last match they played for caching. Every loop, players
get scanned to see if they have a newer match, which will
then update the cache file with that match ID and post
an embed into the WebHooked channel.
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

    DELAY_GAP = 60
    OPENDOTA_API = "https://api.opendota.com/api"
    OPENDOTA_URL = "https://opendota.com/matches"
    HERO_FILE = "heroes.json"
    HEADERS = {
        'Content-Type': 'application/json',
        'User-Agent':   'Dota 2 scraper bot, contact steven(dot)leibrock(at)gmail(dot)com',
    }

    JOKES1 = {
        "Wraith King":      "SKELETON KING",
        "Queen of Pain":    "s4 Cop",
        "Leshrac":          "Shrack",
        "Bristleback":      "Bristlebutt",
        "Nature's Prophet": "Admiral Bulldog",
        "Pudge":            "Dendi",
        "Phoenix":          "Firequacker",
        "Tiny":             "Tony",
        "Io":               "Wisp",
        "Omniknight":       "Sir Action Slacks",
        "Tidehunter":       "Sheever",
        "Storm Spirit":     "Blitz Spirit",
        "Spirit Breaker":   "Space Cow",
        "Vengeful Spirit":  "Vengeful Chicken",
        "Monkey King":      "Mankey Kang",
    }

    JOKES2 = {
        "Wraith King":      "DEATH IS MY BITCH",
        "Ogre Magi":        "c00s GOD",
        "Skywrath Mage":    "From the Ghastly Eeyrie...",
        "Kunkka":           "No room to swing a cat in this crowd",
        "Puck":             "Do you remember the million dollar dream carl?",
        "Legion Commander": "FIGHT ME",
        "Venomancer":       "With Vim and Venom",
        "Lycan":            "WOOF WOOF",
        "Monkey King":      "SKE-DOOSH",
        "Shadow Shaman":    "MY ANCESTORS",
        "Nature's Prophet": "+4 Treants",
        "Undying":          "Left 4 Dead",
        "Spirit Breaker":   "17%",
        "Anti-Mage":        "CS LUL",
    }
    
    def __init__(self, name):
        super(DotaBot, self).__init__(name)
        self.heroes     = list()
        self.filegen    = self._create_filegen("shared")
        self.herojson   = self.filegen(self.HERO_FILE)
        self.match_url  = self._load_match_url()
        self.SLEEP_TIME = 60 * 60 # refresh every hour

        # Prefab the hero data via http GET or local file
        self._load_hero_data()

    def _load_match_url(self):
        "Load up a match URL from the key settings"
        url = self.keydata.get("match_url", self.OPENDOTA_URL)
        if not url.startswith("http"):
            raise IOError("Invalid key given for 'match_url': not http(s)")
        return url

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
    def percent(a=0, b=0, d=1):
        "Convert (a+b)/d to a 1.23 float"
        if d == 0:
            return 0
        return round(((a+b)/float(d))*100.0, 2)

    @staticmethod
    def get_timestr(seconds_i):
        "Create a [H:]M:S string from seconds"
        minutes = seconds_i // 60
        seconds = f"{seconds_i % 60}".zfill(2)
        hours = ""
        if minutes > 59:
            hours = f"{minutes // 60}:"
            minutes = f"{minutes % 60}".zfill(2)
        return f"{hours}{minutes}:{seconds}"

    def get_last_match(self, player_path):
        """
        Get the last match from a given file
        Yield a pair of strings (Match ID * Dota ID * String) when the match
        differs from the cache
        If not newer, return (None * None * Error String)
        """
        if not player_path.is_file():
            return (None, None, "Invalid Path() given for get_last_match()")

        # Read the player's profile file
        with open(player_path, 'r') as f:
            player_data = jload(f)
        
        dota_id    = player_data.get('dota_id', "")
        last_match = player_data.get('last_match', 0)
        
        # If there's no ID at all, just stop
        if not dota_id:
            return (None, None, "Invalid dota ID string")

        resp = get(f"{self.OPENDOTA_API}/players/{dota_id}/matches?limit=1")
        if resp.status_code != 200:
            return (None, None, f"Couldn't load matches for {dota_id}")

        data = resp.json()
        if not data:
            return (None, None, "No matches to be found (???)")
        
        match_id = data[0].get('match_id', 0)
        if match_id == 0:
            return (None, None, "Failed to find any new matches")
        
        if match_id != last_match:
            with open(player_path, 'w') as f:
                data = {'dota_id': dota_id, 'last_match': match_id}
                jdump(data, f)
                return (match_id, dota_id, "")
        return (None, None, f"No new matches for {dota_id}")
                
    def get_payload(self, match_id, dota_id):
        """
        Craft an embed payload for the Discord endpoint
        Returns either a (None * Error String) or (Dictionary * Null String)
        """
        resp = get(f"{self.OPENDOTA_API}/matches/{match_id}")
        if resp.status_code != 200:
            return (None, "Failed to get data from OpenDota API")

        jsonblob = resp.json()
        data     = dict()
        embs     = list()
        
        # Game dependent variables
        players       = jsonblob["players"]
        radiant_win   = jsonblob["radiant_win"]
        game_mode     = jsonblob["game_mode"]
        scores        = (jsonblob["radiant_score"], jsonblob["dire_score"])
        duration      = self.get_timestr(jsonblob["duration"])
        
        # Find the player (or not, then just fail)
        player = None
        for p in jsonblob["players"]:
            if str(p["account_id"]) == dota_id:
                player = p
        if player is None:
            return (None, "Failed to find the player ID in the match")

        # Player variable declarations for use later
        k, a, d     = player['kills'], player['assists'], player['deaths']
        team        = player["isRadiant"]
        pname       = player["personaname"]
        hero_name   = self.find_hero(player["hero_id"])
        
        # Score of game
        wlt = ["Radiant", "~~Dire~~"]  # use strikethrough to show who lost
        if not radiant_win:
            wlt = ["~~Radiant~~", "Dire"]
        embs.append({
            "name"  : "Final Score",
            "value" : f"{wlt[0]} **{scores[0]}** - **{scores[1]}** {wlt[1]}",
            "inline": True
        })
    
        # Player Stats field
        pt = self.percent(k, a, scores[0 if team else 1])
        embs.append({
            "name"  : "Stats (KDA)",
            "value" : f"{k}/{d}/{a} ({pt}% of team)",
            "inline": True
        })
        
        # replay sensitive data is still tagged in the JSON output
        # such that trying to access a replay tag will always be None or some_value
        # Use <dictproperty>.get(key, <default_value>) to request a value
        # and check if the data is there (it will be None otherwise)

        # ping details
        pings = player.get('pings', None)
        if pings is not None:
            tp = sum([p.get('pings', 0) for p in players
                      if p.get("isRadiant") == team])
            pingpc = self.percent(pings, 0, tp)
            embs.append({
                "name"  : "Total Pings",
                "value" : f"{player.get('pings', 0)} ({pingpc}% of team)",
                "inline": True
            })

        # rune details - fetch the bounty rune stuff
        runes = player.get('runes', None)
        if runes is not None:
            total_bounties = sum([p['runes'].get('5', 0) for p in players])
            bountypc = self.percent(runes.get('5', 0), 0, total_bounties)
            embs.append({
                "name"  : "Bounties Collected",
                "value" : f"{runes.get('5', 0)} ({bountypc}% of game)",
                "inline": True
            })

        # Fetch a random quote from the match
        chat = jsonblob.get('chat', None)
        if chat is not None:
            user_lines = [l.get('key', '') for l in chat
                          if l.get('unit', '') == pname]
            if user_lines:
                embs.append({
                    "name"  : "Random Quote",
                    "value" : f"*{choice(user_lines)}* -{pname}",
                    "inline": True
                })
        
        # craft the main embed
        hname = self.JOKES1.get(hero_name, hero_name)
        winstatus = "won" if team is radiant_win else "lost"
        data["embeds"] = [{
            "title"      : f"Results for Match #{match_id}",
            "description": f"{pname} {winstatus} as {hname} ({duration})",
            "url"        : f"{self.OPENDOTA_URL}/{match_id}",
            "color"      : match_id % 0xffffff,
            "fields"     : embs,
            "footer": {
                "text": self.JOKES2.get(hero_name, "Provided by OpenDota API")
            }
        }]
        return (data, "")

    def post_payload(self, data):
        "Send a data dict to the Discord endpoint"
        if not data:
            self.logger("Invalid payload, nothing sent")
            return False
        re = post(self.endpoint, json=data, headers=self.HEADERS)
        if re.status_code != 204:
            return self.logger("Failed to post match")
        return re

    def main(self):
        self.logger(f"Heroes loaded: {len(self.heroes)}")
        files = [f for f in self.filegen().iterdir() if f"{f}".endswith("dota")]
        self.logger(f"Keys: {files}")
        for keypath in files:
            sleep(self.DELAY_GAP)
            self.logger("Fetching most recent match")
            last_match, dota_id, err = self.get_last_match(keypath)
            if last_match is None:
                self.logger(err)
                continue

            self.logger("Posting match")
            payload, err = self.get_payload(last_match, dota_id)
            if payload is None:
                self.logger(err)
                continue
            self.post_payload(payload)
        self.logger("Finished looping")

if __name__ == "__main__":
    bot = DotaBot("dota-bot")
    bot.run()
# end
