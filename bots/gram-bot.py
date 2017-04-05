#!/usr/bin/env python

"""
Instagram Bot

Follow public instagram accounts via WebHooks to Discord
"""

from json import loads
from time import sleep
from Bot import WebHookBot
from requests import get
from bs4 import BeautifulSoup as BS


"""
Steps:

1) load the insta page through BeautifulSoup
2) scrape all <script> tags and look for "sharedData"
3) Strip that text and convert it to a JSON dict
4) use this

images = jsonthing["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]

5) Take caption, ID, image URL off of each object in that list
6) Check the ID against the cache to see if it's new
7) Upload into Discord embed json object and post it away!
"""

class GramBot(WebHookBot):
    ROOT_URL = "https://instagram.com"

    def __init__(self, name):
        super(GramBot, self).__init__(name)
        self.shared = self._create_filegen("shared")
        self.cache = self._create_filegen(name)

    @staticmethod
    def get_latest_image(self, username):
        url = f"{self.ROOT_URL}/{username}"
        resp = get(url)
        if resp.status_code != 200:
            return None

        bs = BS(resp.text, 'html.parser')
        scripts = bs.find_all("script")
        if not scripts:
            return None

        scriptf = [s.text for s in scripts if "sharedData" in s.text]
        blob = loads(scriptf[0][21:-1]) # grabs JSON in the script tag
        images = blob["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
        return images[0]

    def main(self):

        user_list = self.shared("list.instagram")
        if not user_list.is_file():
            return self.logger("User repository list not available")

        users = user_list.read_text().split("\n")
        for user in users:
            self.logger(f"scanning {user}'s instagram")
            cache = self.cache(f"{user}.gramcache")
            cache_s = cache.read_text().strip("\n")
            if not cache_s.isnumeric():
                cache_v = int(cache_s) 
            last_img = self.get_latest_image(user)
            if not int(last_img["id"]) > cache_v:
                continue
            sleep(30)
        pass


if __name__ == "__main__":
    b = GramBot("gram-bot")
    b.run()
    pass

# end
    
