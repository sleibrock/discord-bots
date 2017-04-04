#!/usr/bin/env python
#-*- coding: utf-8 -*-

from random import randint, choice
from Bot import ChatBot
from requests import get
from bs4 import BeautifulSoup as BS

class DumbBot(ChatBot):
    def __init__(self, name):
        super(DumbBot, self).__init__(name)
        self.filegen = self._create_filegen("shared")

    @ChatBot.action
    async def howto(self, args, mobj):
        """
        Return a link to a command reference sheet
        If you came here from !howto help, you're out of luck
        """
        return await self.client.send_message(mobj.channel, "https://google.com/")
        
    @ChatBot.action
    async def dota_id(self, args, mobj):
        """
        Register a Dota ID
        Example: !yt 40281889
        """
        p = self.filegen(f"{mobj.author.id}.dota")
        if not args:
            if p.is_file():
                with open(p, 'r') as f:
                    return self.client.send_message(mobj.channel, f"Current ID: {f.read()}")
                pass
            else:
                return self.client.send_message(mobj.channel, "No Dota ID supplied")

        # Get the first argument in the list and check if it's valid
        u = args[0].strip().strip("\n")
        if len(u) > 30 or not u.isnumeric():
            return self.client.send_message(mobj.channel, "Invalid ID given")

        # Write to file
        with open(p, 'w') as f:
            f.write(u)

        return await self.client.send_message(mobj.channel, f"Registered ID {u}")

    @ChatBot.action
    async def coin(self, args, mobj):
        """
        Do a coin flip
        Example: !coin
        """
        return await self.client.send_message(mobj.channel, choice(["Heads", "Tails"]))

    @ChatBot.action
    async def rtd(self, args, mobj):
        """
        Roll the dice - !rtd <Num of dice> <Num of sides>
        Example: !rtd 10 3
        """
        if len(args) != 2:
            return await self.client.send_message(mobj.channel, "Invalid arg amount")

        if not all((x.isnumeric() for x in args)):
            return await self.client.send_message(mobj.channel, "Non-numeric args given")

        nums = [int(x) for x in args]

        if not all([n for n in nums if 0 < n < 101]):
            return await self.client.send_message(mobj.channel, "Invalid ranges given")

        numd, sides = nums[:2]
        results = [str(randint(1, sides)) for i in range(numd)]
        
        self.logger("Sending message")
        return await self.client.send_message(mobj.channel, ", ".join(results))

    @ChatBot.action
    async def yt(self, args, mobj):
        """
        Get the first Youtube search result video
        Example: !yt how do I take a screenshot
        """
        if not args:
            return await self.client.send_message(mobj.channel, "Empty search terms")

        url = f"https://www.youtube.com/results?search_query={' '.join(args)}"
        resp = get(url)
        if resp.status_code != 200:
            return await self.client.send_message(mobj.channel, "Failed to retrieve search")

        # Build a BS parser and find all Youtube links on the page
        bs = BS(resp.text, "html.parser")
        items = bs.find("div", id="results").find_all("div", class_="yt-lockup-content")
        if not items:
            return await self.client.send_message(mobj.channel, "No videos found")

        # Construct an easy list of URLs
        hrefs = [u for u in [i.find("a", class_="yt-uix-sessionlink")["href"] for i in items]
                 if u.startswith("/watch")]

        # Check if we have any at all
        if not hrefs:
            return await self.client.send_message(mobj.channel, "No URLs found (? wat)")

        # Finish by sending the URL out
        return await self.client.send_message(mobj.channel, f"https://www.youtube.com{hrefs[0]}")

    @ChatBot.action
    async def spam(self, args, mobj):
        """
        Spam a channel with dumb things
        Example: !spam :ok_hand:
        """
        if not args or len(args) > 10:
            return await self.client.send_message(mobj.channel, "Invalid spam input")

        y = args * randint(5, 20)
        return await self.client.send_message(mobj.channel, f"{' '.join(y)}")

    @ChatBot.action
    async def test(self, args, mobj):
        """
        THIS
        DOES
        NOTHING
        """
        self.logger(f"args: {args}")
        return await self.client.send_message(mobj.channel, "Hi")

if __name__ == "__main__":
    d = DumbBot("dumb-bot")
    d.run()
    pass

# end
