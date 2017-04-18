Discord Bots
============

A collection of Robots for Discord.

### Docs

* [AsyncIO Docs](https://docs.python.org/3.4/library/asyncio.html)
* [Discord.py API](http://discordpy.readthedocs.io/en/latest/api.html)
* [Discord Dev Portal](https://discordapp.com/developers/docs/intro)

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
* Racket 6.5 (for the `superv` manager)
* Pip for Python
* `virtualenv` installed from Pip
* Your own set of Discord credentials to use with Bots

Bots can be copied freely from the source code if you just wish to make a bot. 
However running this repository requires the above listed requirements.

### Setup

The code can be cloned entirely from the Git repository and set up with Pip.

```bash
git clone https://gitlab.com/sleibrock/discord-bots.git && cd discord-bots
virtualenv dev
source dev/bin/activate # source dev/Scripts/activate for Windows
make setup
make run
```

If you are using Chat Bots, you need to authorize Bot applications on your
developer page and copy the access token to a local file. If you are using
a WebHook bot, you need to create a WebHook endpoint on a targeted channel
and save that URI to a local file.

### Bots Maintained Currently

Here's the list of bots under development.

* `dumb-bot`, a basic bot to integrate with the rest of the project
* `dota-bot`, an automated daemon to send Dota match info through WebHooks

Other bots are currently being ported from an older library, have been removed, 
or are just undergoing plain old experimentation for the time being. Disabled bots
lie in the `junkyard` folder.
