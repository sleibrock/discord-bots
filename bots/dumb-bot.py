#!/usr/bin/env python
#-*- coding: utf-8 -*-

from random import randint, choice
from Bot import ChatBot
from requests import get
from bs4 import BeautifulSoup as BS

class DumbBot(ChatBot):
    """
    Dumb Bot is a basic toy bot integration
    He has some built in functionality as well as webhook-bot
    integrations to provide a connection to webhooks

    WebHook data is stored in the 'shared' folder, so we
    allow Dumb Bot to access the shared pool
    """

    STATUS = "I'm a bot, Beep Bloop!"

    # Used to convert chars to emojis for /roll
    emojis = {f"{i}":x for i, x in enumerate([f":{x}:" for x in
        ("zero", "one", "two", "three", "four", 
         "five", "six", "seven", "eight", "nine")])}

    def __init__(self, name):
        super(DumbBot, self).__init__(name)
        self.filegen = self._create_filegen("shared")

    @ChatBot.action
    async def howto(self, args, mobj):
        """
        Return a link to a command reference sheet
        If you came here from !howto help, you're out of luck
        """
        output = "Thank you for choosing Dumb Bot™ for your channel\n"
        output += "Here are the available commands\n\n"
        for c in [f"{k}" for k in self.ACTIONS.keys()]:
            output += f"* {c}\n"
        output += "\nFor more info on each command, use '!command help'"
        return await self.message(mobj.channel, self.pre_text(output))

    @ChatBot.action
    async def status(self, args, mobj):
        """
        Change the bot's status to a given string
        Example: !status haha ur dumb
        """
        return await self.set_status(" ".join(args))
        
    @ChatBot.action
    async def dota(self, args, mobj):
        """
        Register a Dota ID
        Example: !yt 40281889
        """
        p = self.filegen(f"{mobj.author.id}.dota")
        if not args:
            if p.is_file():
                return await self.message(mobj.channel, f"ID: {p.read_text()}")
            return await self.message(mobj.channel, "No Dota ID supplied")

        # Get the first argument in the list and check if it's valid
        u = args[0].strip().strip("\n")
        if len(u) > 30 or not u.isnumeric():
            return await self.message(mobj.channel, "Invalid ID given")

        # Write to file and finish
        p.write_text(u)
        return await self.message(mobj.channel, f"Registered ID {u}")

    @ChatBot.action
    async def coin(self, args, mobj):
        """
        Do a coin flip
        Example: !coin
        """
        return await self.message(mobj.channel, choice([":monkey:", ":snake:"]))

    @ChatBot.action
    async def roll(self, args, mobj):
        """
        Make a roll (similar to Dota 2's /roll) between [1..1000]
        Example: !roll 100
        """
        if not args or len(args) > 1:
            return await self.message(mobj.channel, "Invalid arg count")

        x, = args
        if not x.isnumeric():
            return await self.message(mobj.channel, "Non-numeric arg given")

        num = int(x) # bad 
        if num < 1 or num > 1000:
            return await self.message(mobj.channel, "Invalid range given")

        res = [self.emojis[x] for x in str(randint(1, num)).zfill(len(x))]
        return await self.message(mobj.channel, "".join(res))

    @ChatBot.action
    async def yt(self, args, mobj):
        """
        Get the first Youtube search result video
        Example: !yt how do I take a screenshot
        """
        if not args:
            return await self.message(mobj.channel, "Empty search terms")

        url = f"https://www.youtube.com/results?search_query={' '.join(args)}"
        resp = get(url)
        if resp.status_code != 200:
            return await self.message(mobj.channel, "Failed to retrieve search")

        # Build a BS parser and find all Youtube links on the page
        bs = BS(resp.text, "html.parser")
        items = bs.find("div", id="results").find_all("div", class_="yt-lockup-content")
        if not items:
            return await self.message(mobj.channel, "No videos found")

        # Construct an easy list of URLs
        hrefs = [u for u in [i.find("a", class_="yt-uix-sessionlink")["href"] for i in items]
                 if u.startswith("/watch")]

        # Check if we have any at all
        if not hrefs:
            return await self.message(mobj.channel, "No URLs found (? wat)")

        # Finish by sending the URL out
        return await self.message(mobj.channel, f"https://www.youtube.com{hrefs[0]}")

    @ChatBot.action
    async def spam(self, args, mobj):
        """
        Spam a channel with dumb things
        Example: !spam :ok_hand:
        """
        if not args or len(args) > 10:
            return await self.message(mobj.channel, "Invalid spam input")
        y = args * randint(5, 20)
        return await self.message(mobj.channel, f"{' '.join(y)}")

if __name__ == "__main__":
    d = DumbBot("dumb-bot")
    d.run()
    pass

# end
