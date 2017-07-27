#!/usr/bin/env python
#-*- coding: utf-8 -*-

from Bot import ChatBot
from requests import get
from bs4 import BeautifulSoup as BS

class EcoBot(ChatBot):
    '''
    EcoBot (Economy Bot) is a price fetcher upon-request bot
    He has a few commands, each one tied to the different market
    Searches are implemented based on relative ease and so on
    Results should be posted in USD (or whatever currency is relevant)
    '''

    PREFIX               = '$'
    STATUS               = f'{PREFIX}help for info'
    STEAM_SEARCH_URL     = 'http://steamcommunity.com/market/search?q={}'
    STOCKS_SEARCH_URL    = ''
    RUNESCAPE_SEARCH_URL = ''

    def __init__(self, name):
        super(EcoBot, self).__init__(name)

    @ChatBot.action('<item name>')
    async def steam(self, args, mobj):
        '''
        Search Steam market for an item
        Example: $steam redline ak
        '''
        url  = self.STEAM_SEARCH_URL.format('+'.join(args))
        resp = get(url)
        if resp.status_code != 200:
            return await self.message(mobj.channel, f'Failed search (status: {resp.status_code})')

        search_bs    = BS(resp.text, 'html.parser')
        item_listing = search_bs.find_all('a', class_='market_listing_row_link')
        if not item_listing:
            return await self.message('Failed to find any items')

        url_first_item = item_listing[0].get('href', None)
        if url_first_item is None:
            return await self.message('Error scraping item URL')

        """
        # use this later
        resp2 = get(url_first_item)
        if resp2.status_code != 200:
            return await self.message(mobj.channel, f'Failed search (status: {resp.status_code})')
        bsp2  = BS(resp2.text, 'html.parser')
        """
        price = item_listing[0].find_all('span', class_='normal_price')
        msg = [
            f"Name: {item_name}",
            f"Price: {price}",
            f"URL: {url_first_item}",
        ]
        return await self.message(mobj.channel, '\n'.join(msg))

    @ChatBot.action('<item name>')
    async def scape(self, args, mobj):
        '''
        Search RuneScape 3's Grand Exchange
        Example: $scape nature rune
        '''
        return await self.message(mobj.channel, 'Not implemented')

    @ChatBot.action('<stock ID>')
    async def stock(self, args, mobj):
        '''
        Search the actual stock market
        Example: $stock GOOG
        '''
        return await self.message(mobj.channel, 'Not implemented')

    # end bot def

if __name__ == '__main__':
    d = EcoBot('eco-bot')
    d.run()
    pass
    
# end

    
