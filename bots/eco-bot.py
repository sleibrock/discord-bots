#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Bot import ChatBot
from requests import get
from bs4 import BeautifulSoup as BS

class EcoBot(ChatBot):
    """
    EcoBot (Economy Bot) is a price fetcher upon-request bot
    He has a few commands, each one tied to the different market
    Searches are implemented based on relative ease and so on
    Results should be posted in USD (or whatever currency is relevant)
    """

    PREFIX               = "$"
    STATUS               = "{PREFIX}help for info"
    STEAM_SEARCH_URL     = "http://steamcommunity.com/market/search?q={}"
    STOCKS_SEARCH_URL    = ""
    RUNESCAPE_SEARCH_URL = ""

    def __init__(self, name):
        super(EcoBot, self).__init__(name)

    @ChatBot.action('<item name>')
    async def steam(self, args, mobj):
        pass

    @ChatBot.action('<item name>')
    async def scape(self, args, mobj):
        pass

    @ChatBot.action('<stock ID>')
    async def stock(self, args, mobj):
        pass

    # end bot def

if __name__ == '__main__':
    d = EcoBot('eco-bot')
    d.run()
    pass
    
# end

    
