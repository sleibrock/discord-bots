#!/usr/bin/env python
#-*- coding: utf-8 -*-

from sys import exc_info
import asyncio
from time import strftime, localtime
from pathlib import Path
from time import sleep
from json import load as jload, dump as jdump

from discord import Client, Game

"""
The new and improved class-based Bot library

Bots are broken down into two categories: Chat and Webhook

Chat: a bot that receives and can send messages through guilds
Webhook: a bot that can only send messages to specified channel

ChatBots require an authorized Discord application token, while a
WebHookBot only requires an endpoint acquired from setting up a
Webhook on a specific Discord Guild channel. Both can be useful in
different scenarios (Webhook is better at automated tasks, while
Chat is better at replying to user requests (and also voice)).
"""

class Bot(object):
    """
    The main Bot class for all bots to inherit from
    The Bot class holds any and most static variables to use
    across all the bots
    """

    BOT_FOLDER = "botdata"
    KEY_FOLDER = "keys"
    SHARED = "shared"
    LOGSTR = "[\033[38;5;{3}m{0:<12}\033[0m @ {1}] {2}"

    URLMAP = {" ": "%20", "'": "%27", "`": "%60", "%": "%25", "&": "%26",
              "!": "%21", "@": "%40", "#": "%23", "$": "%24", "+": "%2B",
              "*": "%2A", "^": "%5E", "(": "%28", ")": "%29", "=": "%3D",
              "[": "%5B", "]": "%5D", "{": "%7B", "}": "%7D"}
    
    BADWORDS = ('fuck', 'cock', 'shit', 'piss', 'wank', 'kiddy', 'child',
                'porn', 'masturbate', 'bate', 'anal', 'cum')

    # Static methods will come first
    @staticmethod
    def replace(string="", char_map=URLMAP):
        "Replace a string with URL safe characters (' ' => '%20')"
        s = string
        for k, v in char_map.items():
            s.replace(k, v)
        return s
    
    @staticmethod
    def has_badwords(string=""):
        "Determine if a string has a bad word in it"
        if not string:
            return False
        return any((x in string for x in Bot.BADWORDS))

    @staticmethod
    def _make_folder(path):
        "Make a folder if it doesn't exist and isn't a file"
        if not path.is_dir() and not path.is_file():
            path.mkdir()
            return True
        return False

    @staticmethod
    def _create_logger(bot_name):
        """
        Create a pretty-format printer for bots to use
        Bots will use colors in the range of 16-256 based on their hash modulo
        """
        color = 16 + (hash(bot_name) % 240)
        def logger(msg):
            print(Bot.LOGSTR.format(bot_name, strftime("%H:%M:%S", localtime()), msg, color))
            return True
        return logger

    @staticmethod
    def _create_filegen(bot_name):
        """
        Create a function to generate file Paths for us
        If no filename was given, yield the path to the folder instead
        """
        Bot._make_folder(Path(Bot.BOT_FOLDER))
        Bot._make_folder(Path(Bot.BOT_FOLDER, bot_name))
        def bot_file(filename=None):
            if filename is None or filename == "":
                return Path(Bot.BOT_FOLDER, bot_name)
            return Path(Bot.BOT_FOLDER, bot_name, filename)
        return bot_file

    @staticmethod
    def _read_file(path):
        "Attempt to read a file from a Path"
        if not path.is_file():
            raise IOError
        with open(path, 'r') as f:
            return f.read()
        return None 

    @staticmethod
    def pre_text(msg, lang=None):
        "Encapsulate a string in a <pre> container"
        s = "```{}```"
        if lang is not None:
            s = s.format(format+"\n{}")
        return s.format(msg.rstrip().strip("\n").replace("\t", ""))

    # Instance methods go below __init__()
    def __init__(self, name):
        self.name = name
        self.logger = self._create_logger(self.name)

    def read_key(self):
        """
        Read a bot's key JSON to get it's token/webhook link
        Keys must be stored in the key folder and have a basic 'key':'<keytext>' object
        """
        with open(Path(self.KEY_FOLDER, f'{self.name}.key'), 'r') as f:
            datum = jload(f)
            key = datum.get("key", "")
            if not key:
                raise IOError("Key not found in JSON keyfile")
            return key
        return None

class ChatBot(Bot):
    """
    The ChatBot is a wrapper for the Discord client itself
    Any bots that take user input from a channel will inherit this
    
    In order to create a Discord Client, a bot has to have an authorized
    token associated with it. The keys are read from files (no trailing newlines)
    inside of a local "keys" folder. The "keys" folder is at the root of the 
    project, not inside the Bot Data folder
    
    NOTE: when instancing, don't create more than one instance at a time
    """
    PREFIX    = "!"
    ACTIONS   = dict()
    HELPMSGS  = dict()
    BLACKLIST = "blacklist"
    BANS      = dict()

    # Bad words to prevent malicious searches from a host device
    BADWORDS = ["fuck", "cock", "child", "kiddy", "porn", "pron", "pr0n",
                "masturbate", "bate", "shit", "piss", "anal", "cum", "wank"]

    # Change this to adjust your default status setting (loads in on_ready())
    STATUS    = "Beep bloop!"

    @staticmethod
    def action(help_msg=""):
        """
        Decorator to register functions into the action map
        This is bound to static as we can't use an instance object's method
        as a decorator (could be a classmethod but who cares)
        """
        def regfunc(function):
            if callable(function):
                if function.__name__ not in ChatBot.ACTIONS:
                    fname = f'{ChatBot.PREFIX}{function.__name__}'
                    ChatBot.ACTIONS[fname] = function
                    ChatBot.HELPMSGS[fname] = help_msg.strip()
                    return True
            return function
        return regfunc
    
    @staticmethod
    def get_emojis(msg_obj):
        "Fetch emojis from a Message object"
        if msg_obj.server is not None:
            return msg_obj.server.emojis
        return list()

    # Instance methods below
    def __init__(self, name):
        super(ChatBot, self).__init__(name)
        self.actions = dict()
        self.client = Client()
        self.token = self.read_key()
        self._load_bans()

    async def message(self, channel, string):
        """
        Shorthand version of client.send_message
        So that we don't have to arbitrarily type 
        'self.client.send_message' all the time
        """""
        return await self.client.send_message(channel, string)

    def _load_bans(self):
        "Load the banfile and convert it to a blacklist"
        p = Path(self.BLACKLIST)
        if not p.is_file():
            return self.logger("Local blacklist not found")
        with open(p, 'r') as f:
            self.BANS = jload(f)
        self.logger("Initial banned users:")
        for k, v in self.BANS.items():
            self.logger(f"* {k}")
        return

    @staticmethod
    def convert_user_tag(tag_str):
        "Convert a string <@(?){0,1}[0-9]> to [0-9] (False if invalid)"
        print(f"Given: {tag_str}")
        if not tag_str.startswith("<@") and not tag_str.endswith(">"):
            return False
        inside = tag_str[(3 if tag_str.startswith("<@!") else 2):-1]
        if not inside.isnumeric():
            return False
        return inside

    def display_no_servers(self):
        """
        If the bot isn't connected to any servers, show a link
        that will let you add the bot to one of your current servers
        """
        if not self.client.servers:
            self.logger(f"Join link: {discord.utils.oauth_url(self.client.user.id)}")
        return

    def add_ban(self, ban_target):
        "Add a user to the bans and dump the dict (True=Added, False=Not)"
        if ban_target in self.BANS:
            return False
        self.BANS[ban_target] = True
        with open(Path(self.BLACKLIST), 'w') as f:
            jdump(self.BANS, f)
        return True

    def del_ban(self, ban_target):
        "Remove a user from the bans and update the file"
        if ban_target not in self.BANS:
            return False
        self.bans.pop(ban_target)
        with open(Path(self.BLACKLIST), 'w') as f:
            jdump(self.BANS, f)
        return True

    def is_banned(self, userid):
        "Return whether a user is banned or not"
        return userid in self.BANS

    @staticmethod
    def is_admin(mobj):
        "Return whether user is an administrator or not"
        return mobj.channel.permissions_for(mobj.author).administrator

    def get_last_message(self, chan, uid=None):
        """
        Search the given channel for the second-to-last message
        aka: the message before the command was given to the bot
        """
        if len(self.client.messages) == 0:
            raise Exception("Wat")
        if len(client.messages) == 1:
            return None
        c_uid = lambda u, v: True
        if uid is not None:
            c_uid = lambda u, v: u == v
        res = [msg for msg in self.client.messages
               if msg.channel == chan
               and msg.author.id != self.client.user.id
               and c_uid(uid, msg.author.id)]
        if len(res) <= 1:
            return None
        return res[-2]

    async def set_status(self, string):
        "Set the client's presence via a Game object"
        return await self.client.change_presence(game=Game(name=string))

    def event_ready(self):
        "Change this event to change what happens on login"
        async def on_ready():
            self.display_no_servers()
            await self.set_status(self.STATUS)
            return self.logger(f"Bot online, {len(self.ACTIONS)} commands loaded")
        return on_ready

    def event_error(self):
        "Change this for better error logging if needed"
        async def on_error(evt, *args, **kwargs):
            self.logger(f"Discord error in '{evt}''")
            return self.logger(exc_info())
        return on_error

    def event_message(self):
        "Change this to change overall on message behavior"
        async def on_message(msg):
            args = msg.content.strip().split(" ")
            key = args.pop(0).lower() # messages sent can't be empty
            if key in self.ACTIONS:
                if self.is_banned(msg.author.id):
                    self.logger("Banned user attempted command")
                    return await self.client.delete_message(msg)
                return await self.ACTIONS[key](self, args, msg)
            return
        return on_message

    def setup_events(self):
        """
        Set up all events for the Bot
        You can override each event_*() method in the class def
        """
        self.client.event(self.event_message())
        self.client.event(self.event_error())
        self.client.event(self.event_ready())

    def run(self):
        """
        Main event loop
        Set up all Discord client events and then run the loop
        """
        self.setup_events()
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.client.start(self.token))
        except Exception as e:
            self.logger(f"Caught an exception: {e}")
        except SystemExit:
            self.logger(f"System Exit signal")
            print("System Exit signal")
        except KeyboardInterrupt:
            self.logger("Keyboard interrupt signal")
        finally:
            self.logger(f"{self.name} quitting")
            loop.run_until_complete(self.client.logout())
            loop.stop()
            loop.close()
            quit()
        return


class WebHookBot(Bot):
    """
    A WebHookBot is a bot that will automatically execute actions
    based on a timer and will fire messages towards a Discord endpoint
    These are more of "daemons" one can make to automate multitudes of tasks
    
    NOTE: WebHookBots can not receive user input directly from a Discord channel
    Use a ChatBot to take input from a user and write it to a file a WebHookBot
    can access easily (a "shared" folder), or a microservice like a database,
    memcache or even a messaging queue like Rabbitmq/Zeromq

    (With some changes, WebHook bot could be made to use asyncio/uvloop)
    """
    SLEEP_TIME = 60

    def __init__(self, name):
        super(WebHookBot, self).__init__(name)
        self.endpoint = self.read_key()

    def main(self):
        """
        Override this in your webhook definition
        The main() function must take no arguments
        """
        self.logger(f"I'm a WebHook bot!")

    def run(self):
        """
        Run the program loop
        Override the main() function to change what happens in each loop cycle
        """
        try:
            while True:
                self.main()
                sleep(self.SLEEP_TIME)
            return
        except Exception as e:
            print(e)
            self.logger(f"Exception caught: {e}")
        except SystemExit:
            self.logger("Sys Interrupt")
        except KeyboardInterrupt:
            self.logger("Keyboard Interrupt")
        finally:
            self.logger(f"Shutting down {self.name}")
        return quit()
            
# end 
