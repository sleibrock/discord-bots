#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Janitor-bot

Will clean up old messages and purge channels of certain things
Maybe have some classic Fallout 3 Mr. Handy jokes xd
"""

from botinfo import *

bot_name = "janitor-bot"
client = discord.Client()
logger = create_logger(bot_name)

@client.event
async def on_ready():
    """
    The function that is consumed upon startup
    Set vars, check for bot folder existence, etc
    """
    if not setup_bot_data(bot_name, logger):
        client.close()
        return logger("Failed to set up {}'s folder".format(bot_name))
    return logger("Connection status: {}".format(client.is_logged_in))

@client.event
async def on_error(msg, *args, **kwargs):
    return logger("Discord error: {}".format(msg))

@client.event
async def on_message(msg):
    """
    Dispatch commands to the respective functions
    Map a keyword to a function and pass the message values to the func
    """
    splits = msg.content.lower().strip().split(" ")
    k = splits.pop(0)
    rest = " ".join(splits) if len(splits) > 0 else ""
    args = [rest, discord.utils.get(msg.server.members, id=msg.author.id), msg.channel]
    binds = {'!clean'   : clean_messages,
             '!perms'   : check_perms,}
    if k in binds:
        return await binds[k](*args)
    return

async def check_perms(msg, memb, mch):
    """
    Check a user's permissions
    Print all of the user's permissions in a readable line-by-line format
    """
    try:
        perms = mch.permissions_for(memb)
        lines = [
            "Administrator? {}".format(perms.administrator),
            "Manage server? {}".format(perms.manage_server),
            "Manage messages? {}".format(perms.manage_messages),
            "Attach files? {}".format(perms.attach_files),
            ]
        return await client.send_message(mch, pre_text("\n".join(lines)))
    except Exception as ex:
        logger("!perms: {}".format(ex))
    return await client.send_message(mch, "Failed to check permissions")

async def clean_messages(msg, memb, mch):
    """
    This cleans all messages from the input channel
    This is only a command allowed for administrators
    Optional argument to purge non-images from a channel
    """
    try:
        perms = mch.permissions_for(memb)
        if not perms.administrator:
            return await client.send_message(mch, "Admins only allowed to purge")
        binds = {
            "text" : lambda m: len(m.attachments) == 0,
            }
        l = binds[msg] if msg in binds else None # yank a function to check for
        await client.purge_from(mch, limit=30000, check=l)
        return
    except Exception as ex:
        logger("!clean: {}".format(ex))
    return await client.send_message(mch, "Failed to execute action")

if __name__ == "__main__":
    run_the_bot(client, argv, logger)

# end

