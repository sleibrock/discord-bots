Discord Bots
============

**All code is hosted on GitLab and mirrored to GitHub. Check out [GitLab page](https://gitlab.com/sleibrock/discord-bots.git) instead**

A collection of Robots for Discord.

### Docs

* [AsyncIO Docs](https://docs.python.org/3.4/library/asyncio.html)
* [Discord.py API](http://discordpy.readthedocs.io/en/latest/api.html)
* [Discord Dev Portal](https://discordapp.com/developers/docs/intro)
* [Racket Threading Docs](https://docs.racket-lang.org/reference/threads.html)

### Purpose

The purpose of this project is to

* Create a program that runs multiple programs in parallel
* Create a series of programs that run and interact with chat service Discord in meaningful ways (if even possible)

The development here goes into two areas: the bots, and the supervisor.

### Requirements

To run this project you will need:

* Python 3.6 (for f-strings and improved `dict()` efficiency of course)
* Racket 6.5+ (for the Supervisor program)
* Pip for Python
* `virtualenv` installed from Pip
* Your own set of Discord credentials to use with Bots (see lower for more details)

### Setup

The code can be cloned entirely from the Git repository and set up with Pip.

```
git clone https://gitlab.com/sleibrock/discord-bots.git && cd discord-bots
virtualenv dev
source dev/bin/activate # source dev/Scripts/activate for Windows
pip install -r requirements.txt
make run
```

You will have provide your own credentials to the `keys` folder. My bots right now are not hosted for public use, so you need to create your own applications underneath Discord's developer portal and get a key token per application. Each bot's key should be named `<botname>.key`.

### Supervisor

The Supervisor is a program that will take a list of programs to run, and run them simultaneously alongside eachother. Racket was chosen as it was easiest to prototype a working solution very quickly compared to other languages. Languages I've tried:

* Python - `asyncio` and other such packages lead to mangled, awful looking code
* Rust - almost got a working solution but had problems understanding lifetimes at the time
* Elixir - was able to run subprocesses, but wasn't able to redirect their output to `stdout` live

Right now the Supervisor was written with the intent that the network connection between the bots and the Discord servers themselves would not be stable (ie: my internet drops all the time, so it's hard to keep them running when I'm afk).

So right now, the Supervisor restarts the bots every hour on the dot, and actively checks them every 5 minutes inbetween. The times themselves can be increased or decreased based on need. A configuration file setup will be needed in the future to adjust these values (it's a work in progress).

(Notes about Racket: the Supervisor has gone through many iterations but this one seems to be the most "stable" solution. I've tried multiple Racket implementations using different techniques like `thread-wait`/`thread-receive` but that one didn't really do that well, but using custodian groups and killing them as a means to end all subprocesses turned out to be the most efficient solution code-wise and sanity-wise.)

### Bots

The Bots right now differ from a basic command bot defined by `discord.py`'s library. It used to be that it was hard to define behavior in certain scenarios (like creating timer-based bots that do automatic output based on events), but it might be easier to create bots now as time has moved on.

Bots are created with simple input/output principles such that a channel doesn't really get filled by outside inputs, but strictly from user inputs only. Some bots do fetch data from third parties and parse it to retrieve data, but that's it.

### Long Term Goals

There are several goals in place, some of which I hope I can hit within reasonable time frames.

* Configuration File - adding new Bots works so long as you edit the Racket source. I would like to have a way to work around that by creating a config file to manipulate several Supervisor settings
* Code coverage - make sure code works instead of submitting broken bots all the time
* New backend services - instead of writing to raw files, maybe use a database or in-memory cache
* Hardware Integration - code can already be updated remotely via one of the bots, but other services could be integrated as well for the hardware
* Data/IO Separation - to keep things more pure, I will be working on separating as many pure functions as possible to aid in code testing
* MyPy Typing - I would like to develop a bot using MyPy types to help look for possible bugs as well
* PyLint Code Standards - code is very messy and needs to adhere to better coding standards for sure

### Bots Maintained Actively

These are the bots actively maintained in code. They're all written with Python and open-sourced for anyone to use and edit as they please.

* `dumb-bot`, a bot with very basic functionality
* `hacker-bot`, a bot with some programmer tools
* `dota-bot`, a bot to post latest matches and such nonsense
* `graph-bot`, a bot used to graph mathematical figures
* `janitor-bot`, a bot to take advantage of Discord's bot-only features like bulk-deletes
