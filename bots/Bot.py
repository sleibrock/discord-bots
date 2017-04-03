#!/usr/bin/env python
#-*- coding: utf-8 -*-

import asyncio
from time import strftime, localtime
from pathlib import Path
from time import sleep

import discord
from discord import Embed

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

    # Static methods will come first
    @staticmethod
    def _make_folder(path):
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
            print(Bot.LOGSTR.format(bot_name, strftime("%H:%M%S", localtime()), msg, color))
            return True
        return logger

    @staticmethod
    def _create_filegen(bot_name):
        """
        Create a function to generate file Paths for us
        If no filename was given, yield the path to the folder instead
        """""
        Bot._make_folder(Path(Bot.BOT_FOLDER))
        Bot._make_folder(Path(Bot.BOT_FOLDER, bot_name))
        def bot_file(filename=None):
            if filename is None or filename == "":
                return Path(Bot.BOT_FOLDER, bot_name)
            return Path(Bot.BOT_FOLDER, bot_name, filename)
        return bot_file

    @staticmethod
    def _read_file(path):
        if not path.is_file():
            raise IOError
        with open(path, 'r') as f:
            return f.read()
        return None 

    @staticmethod
    def pre_text(msg, lang=None):
        """
        Encapsulate a string in a <pre> container
        """
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
        Read a bot's keyfile to get it's token/webhook link
        """
        return Bot._read_file(Path(self.KEY_FOLDER, f"{self.name}.key")).strip("\n")


class ChatBot(Bot):
    """
    The ChatBot is a wrapper for the Discord client itself
    Any bots that take user input from a channel will inherit this
    
    In order to create a Discord Client, a bot has to have an authorized
    token associated with it. The keys are read from files (no trailing newlines)
    inside of a local "keys" folder. The "keys" folder is at the root of the 
    project, not inside the Bot Data folder
    """
    PREFIX = "!"

    def __init__(self, name):
        super(ChatBot, self).__init__(self, name)
        self.actions = dict()
        self.client = discord.Client()
        self.token = self.read_key()

    def display_no_servers(self):
        """
        If the bot isn't connected to any servers, show a link
        that will let you add the bot to one of your current servers
        """
        pass

    def action(self, function):
        """
        Decorator to register functions into the action map
        """
        if callable(function):
            if function.__name__ not in self.actions:
                self.actions[f"{PREFIX}{function.__name}"] = function
                return True
        return function

    # Override-able events for your Discord bots
    def event_ready(self):
        async def on_ready():
            self.display_no_servers()
            return self.logger(f"Connection status: {self.client.is_logged_in}")
        return on_ready

    def event_error(self):
        async def on_error(msg, *args, **kwargs):
            return self.logger(f"Discord error: {msg}")
        return on_error

    def event_message(self):
        async def on_message(msg):
            args = msg.content.strip().split(" ")
            key = args.pop(0).lower() # messages sent can't be empty
            if key in self.actions:
                if len(args) >= 1:
                    if args[0].lower() == "help":
                        return await self.client.send_message(
                            msg.channel,
                            self.pre_text(
                                f"Help for '{key}':{self.actions[key].__doc__}"
                            )
                        )
                return await self.actions[key](args, msg)
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
            print(f"Caught an exception: {e}")
        except SystemExit:
            print("System Exit signal")
        except KeyboardInterrupt:
            print("Keyboard Interrupt signal")
        finally:
            print(f"{self.name} quitting")
            loop.run_until_complete(client.logout())
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
    can access easily (a "shared" folder)
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
            self.logger(f"Exception caught: {e}")
        except SystemExit:
            self.logger("Sys Interrupt")
        except KeyboardInterrupt:
            self.logger("Keyboard Interrupt")
        finally:
            self.logger(f"Shutting down {self.name}")
        return quit()
            
        
        
            
# end 
