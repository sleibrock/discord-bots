Discord Bots
============

A collection of Robots for Discord.

[![Build Status](https://travis-ci.org/sleibrock/discord-bots.svg?branch=master)](https://travis-ci.org/sleibrock/discord-bots)
### Docs

* [AsyncIO Docs](https://docs.python.org/3.4/library/asyncio.html)
* [Discord.py API](http://discordpy.readthedocs.io/en/latest/api.html)
* [Discord Dev Portal](https://discordapp.com/developers/docs/intro)
* [Racket Threading Docs](https://docs.racket-lang.org/reference/threads.html)

# Requirements, Installation and Setup

First I'll explain how to set this all up. Then I'll explain the
design behind why I chose to use the tech behind this.

My Discord Bots project requires the following:

* Python 3.5
* Pip
* Racket

The Discord Bots will be written in Python. The tool to run them
all is however, written in Racket. Once you install the required
software, move onto the next stage.

Naturally start with a Git clone

```
git clone https://github.com/sleibrock/discord-bots.git
```

After that we need to enter the directory and run some
setup commands. If you don't have sudo access for some reason,
you can create a virtualenv for the Python packages.

```
virtualenv <venv name> (optional)
make setup
```

This runs a Pip command to install the packages. We use a
third-party Discord API called Discord.py, which includes a
WebSockets toolkit. We also use BeautifulSoup and Requests
for web scraping options in our bots.

If you wanted to run these bots under your own, you would have to
in turn fill out new Bot accounts under Discord's registration. Once
you do that, you need the Bot API tokens. For each program, create a new
key file containing the token string. For `dumb-bot` for example, create a new
file `dumb-bot.key` and put the token in there.

Now, lastly, to run, should be as simple as:

```
make run
```

# Creating a New Bot User

Under Discord's API pages it allows you to create a new application using the API.
From there once you create your application, you can turn it into a Bot User, which
will basically tag a "Bot" label onto it's username for the rest of it's life.

Once you turn it into a bot user, copy the Client ID given by Discord, copy
[this](https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=0)
link and replace the CLIENT_ID with the number Discord assigned your bot. Now you can
add it to a server that you own.

# Plans

* Reading thread to listen for Bot output
* Artwork bot
* Some kind of MUD bot

# Contributing

Follow standard style conventions like 4-space tabs for Python programs, but that's
about it. I don't listen to PEP-8 rules since they get in my way.

# Issues

If a bot is misbehaving, or spits out random errors, post an issue with the command
that caused the output.
