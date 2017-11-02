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


### Requirements

To run this project you will need:

* Python 3.6
* Racket 6.5 (for the `superv` manager)
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

Each bot needs a key in order to use the Discord API. A Chat Bot requires an access token that is assigned when you create a Bot account under your Discord Developer page. A WebHook Bot requires a WebHook URL to post data to. Keys are stored in JSON format for easy loading, so use the following format and store the keys under a `keys/` folder named `<bot-filename>.key`.
```json
{
    "key": "secret_key" # or https:// link for webhook bots
}
```


### Bots Maintained Currently

Here's the list of bots under development.

* `dumb-bot`, a basic bot to integrate with the rest of the project
* `dota-bot`, an automated daemon to send Dota match info through WebHooks
* `eco-bot`, a game-economy assistant to look up prices (early development stages)

Other bots are currently being ported from an older library, have been removed, 
or are just undergoing plain old experimentation for the time being. Disabled bots
lie in the `junkyard` folder.
