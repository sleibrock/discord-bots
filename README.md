Discord Bots
============

A collection of MrDestructoid robots for Discord.

# Requirements, Installation and Setup

First I'll explain how to set this all up. Then I'll explain the 
design behind why I chose to use the tech behind this.

My Discord Bots project requires the following:

* Python 3
* Pip
* Racket

The Discord Bots will be written in Python. The tool to run them 
all is however, written in Racket. Once you install the required 
software, move onto the next stage.

Naturally start with a Git clone

```
git clone https://github.com/sleibrock/discord-bots/git
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

# Bot Manager in Racket

Racket as a standard installation, comes with the ability to create, manage and 
destroy threads very easily. So by this, I created a program which has the ability 
to launch multiple instances of Python programs and watch their threads. I call 
this the Gravekeeper program.

If a Bot fails, from some unhandled exception, IO error, or whatever, Racket will 
check each thread every minute to see if the thread is running. If it isn't, it will 
re-initialize the program that crashed and respawn it in a new thread, and put it back 
into the thread pool.

This was very easy to do in Racket, and doing it in Python would've been much much 
worse. The new Python `asyncio` library might be useful for creating a Python program to 
do this functionality, but I prefer it in Racket for the time being.

The downside may be too much memory gets consumed by Racket since it's a high-level 
interpreted language. I might have to consider compiling it or using typed Racket to 
bring memory use down. The memory usage might get too high for certain smaller devices 
to handle, as this will be hosted on a Raspberry Pi device with only one gigabyte of 
RAM.

# Creating a New Bot User

Under Discord's API pages it allows you to create a new application using the API. 
From there once you create your application, you can turn it into a Bot User, which 
will basically tag a "Bot" label onto it's username for the rest of it's life.

Once you turn it into a bot user, copy the Client ID given by Discord, copy
[this](https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=0) 
link and replace the CLIENT_ID with the number Discord assigned your bot. Now you can 
add it to a server that you own.

# Plans

* RemindMe bot
* Reading thread to listen for Bot output
* Artwork bot
* Some kind of MUD bot

# Contributing

Follow standard style conventions like 4-space tabs for Python programs, but that's 
about it. I don't listen to PEP-8 rules since they get in my way.

# Issues

If a bot is misbehaving, or spits out random errors, post an issue with the command 
that caused the output.
