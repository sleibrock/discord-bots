Discord Bots
============

A collection of Robots for Discord.

### Docs

* [AsyncIO Docs](https://docs.python.org/3.4/library/asyncio.html)
* [Discord.py API](http://discordpy.readthedocs.io/en/latest/api.html)
* [Discord Dev Portal](https://discordapp.com/developers/docs/intro)
* [Racket Threading Docs](https://docs.racket-lang.org/reference/threads.html)

### Introduction

Discord, the popular chat service aimed at gamers, supports a WebSocket API for sending and receiving data. From this we can create Bot users, so this project has the sole focus of creating various bots to be used with the Discord service.

In it's current state, this project has Python code wrapping around the `discord.py` library itself to aid in the development of bots, as well as bots written in Python with many different goals of doing as much as they can.

Currently, there's two types of Bots that can be used with Discord:
* Interactive chat bot - a bot that receives and can send messages to channels
* WebHook bot - a bot that can only send data to a channel via a URI endpoint

Right now this project uses mostly Interactives. WebHooks are being explored.

### Requirements

To run this project you will need:

* Python 3.6
* Racket 6.5
* Pip for Python
* `virtualenv` installed from Pip
* Your own set of Discord credentials to use with Bots

### Setup

The code can be cloned entirely from the Git repository and set up with Pip.

```bash
git clone https://gitlab.com/sleibrock/discord-bots.git && cd discord-bots
virtualenv dev
source dev/bin/activate # source dev/Scripts/activate for Windows
make setup
make run
```

### Bots Maintained Actively

These are the bots actively maintained in code. They're all written with Python and open-sourced for anyone to use and edit as they please.

* `dumb-bot`, a bot with very basic functionality
* `hacker-bot`, a bot with some programmer tools
* `dota-bot`, a bot to post latest matches and such nonsense
* `graph-bot`, a bot used to graph mathematical figures
* `janitor-bot`, a bot to take advantage of Discord's bot-only features like bulk-deletes
