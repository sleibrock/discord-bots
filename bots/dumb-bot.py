#!/usr/bin/env python
#-*- coding: utf-8 -*-

from random import randint, choice
from Bot import ChatBot
from requests import get
from bs4 import BeautifulSoup as BS
from json import dump as jdump

class DumbBot(ChatBot):
    """
    Dumb Bot is a basic toy bot integration
    He has some built in functionality as well as webhook-bot
    integrations to provide a connection to webhooks

    WebHook data is stored in the 'shared' folder, so we
    allow Dumb Bot to access the shared pool
    """

    STATUS = "I'm a bot, Beep Bloop!"
    GIT_URL = "https://github.com/sleibrock/discord-bots"

    # Used to convert chars to emojis for self.roll()
    emojis = {f"{i}":x for i, x in enumerate([f":{x}:" for x in
        ("zero", "one", "two", "three", "four", 
         "five", "six", "seven", "eight", "nine")])}

    def __init__(self, name):
        super(DumbBot, self).__init__(name)
        self.filegen = self._create_filegen("shared")

    @ChatBot.action('<Command>')
    async def help(self, args, mobj):
        """
        Return a link to a command reference sheet
        If you came here from !help help, you're out of luck
        """
        if args:
            key = args[0]
            if not args[0].startswith(ChatBot.PREFIX):
                key = f'{ChatBot.PREFIX}{args[0]}'
            if key in self.ACTIONS:
                t = self.pre_text(f'Help for \'{key}\':{self.ACTIONS[key].__doc__}')
                return await self.message(mobj.channel, t)
        keys = [f'{k}' for k in self.ACTIONS.keys()]
        longest = max((len(s) for s in keys)) + 2
        output = 'Thank you for choosing Dumb Bot™ for your channel\n'
        output += 'Here are the available commands\n\n'
        for c in keys:
            output += f'* {c.ljust(longest)} {self.HELPMSGS.get(c, "")}\n'
        output += f'\nFor more info on each command, use \'{ChatBot.PREFIX}help <command>\''
        output += f'\nVisit {self.GIT_URL} for more info'
        return await self.message(mobj.channel, self.pre_text(output))

    @ChatBot.action('<Status String>')
    async def status(self, args, mobj):
        """
        Change the bot's status to a given string
        Example: !status haha ur dumb
        """
        return await self.set_status(" ".join(args))

    @ChatBot.action('<Dota ID String>')
    async def dota(self, args, mobj):
        """
        Register a Dota ID
        Example: !dota 40281889
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
        with open(p, 'w') as f:
            jdump({'dota_id': u}, f)
        return await self.message(mobj.channel, f"Registered ID {u}")

    @ChatBot.action()
    async def coin(self, args, mobj):
        """
        Do a coin flip
        Example: !coin
        """
        return await self.message(mobj.channel, choice([":monkey:", ":snake:"]))

    @ChatBot.action('<Number>')
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

    @ChatBot.action('[Search terms]')
    async def yt(self, args, mobj):
        """
        Get the first Youtube search result video
        Example: !yt how do I take a screenshot
        """
        if not args:
            return await self.message(mobj.channel, "Empty search terms")
        
        tube = "https://www.youtube.com"
        resp = get(f"{tube}/results?search_query={self.replace(' '.join(args))}")
        if resp.status_code != 200:
            return await self.message(mobj.channel, "Failed to retrieve search")

        # Build a BS parser and find all Youtube links on the page
        bs = BS(resp.text, "html.parser")
        main_d = bs.find('div', id='results')
        if not main_d:
            return await self.message(mobj.channel, 'Failed to find results')

        items = main_d.find_all("div", class_="yt-lockup-content")
        if not items:
            return await self.message(mobj.channel, "No videos found")

        # Loop until we find a valid non-advertisement link
        for container in items:
            href = container.find('a', class_='yt-uix-sessionlink')['href']
            if href.startswith('/watch'):
                return await self.message(mobj.channel, f'{tube}{href}')        
        return await self.message(mobj.channel, "No YouTube video found")

    @ChatBot.action('[String]')
    async def spam(self, args, mobj):
        """
        Spam a channel with dumb things
        Example: !spam :ok_hand:
        """
        if not args or len(args) > 10:
            return await self.message(mobj.channel, "Invalid spam input")
        y = args * randint(5, 20)
        return await self.message(mobj.channel, f"{' '.join(y)}")

    @ChatBot.action('<Poll Query>')
    async def poll(self, args, mobj):
        """
        Turn a message into a 'poll' with up/down thumbs
        Example: !poll should polling be a feature?
        """
        await self.client.add_reaction(mobj, '👍')
        await self.client.add_reaction(mobj, '👎')
        return

    @ChatBot.action('[Users]')
    async def ban(self, args, mobj):
        """
        Ban a user from using bot commands (admin required)
        Example: !ban @Username @Username2 ...
        """
        if not self.is_admin(mobj):
            return await self.message(mobj.channel, "Admin permissions needed")
        bancount = 0
        ids = [self.convert_user_tag(x) for x in args]
        for uid in ids:
            if uid is not False:
                r = self.add_ban(uid)
                bancount += 1 if r else 0
        return await self.message(mobj.channel, f"{bancount} users banned")

    @ChatBot.action('[Users]')
    async def unban(self, args, mobj):
        """
        Unban a user from the bot commands (admin required)
        Example: !unban @Username @Username2 ...
        """
        if not self.is_admin(mobj):
            return await self.message(mobj.channel, "Admin permissions needed")
        unbanc = 0
        ids = [self.convert_user_tag(x) for x in args]
        for uid in ids:
            if uid is not False:
                r = self.del_ban(uid)
                unbanc += 1 if r else 0
        return await self.message(mobj.channel, f"{unbanc} users unbanned")

    @ChatBot.action()
    async def botinfo(self, args, mobj):
        """
        Print out debug information about the bot
        Example: !botinfo
        """
        lines = []

        with open(".git/refs/heads/master") as f:
            head_hash = f.read()[:-1]

        # All the lines used in the output
        lines = [
            f"Name: {self.name}",
            f"Actions loaded: {len(self.ACTIONS)}",
            f"Ban count: {len(self.BANS)}",
            f"Commit version: #{head_hash[:7]}",
            f"Commit URL: {self.GIT_URL}/commit/{head_hash}"
        ]
        return await self.message(mobj.channel, "```{}```".format("\n".join(lines)))

if __name__ == "__main__":
    d = DumbBot("dumb-bot")
    d.run()
    pass

# end
