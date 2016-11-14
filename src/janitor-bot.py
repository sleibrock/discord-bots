#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Janitor-bot

Will clean up old messages and purge channels of certain things
"""

from botinfo import *
from random import choice

bot_name = "janitor-bot"
client = discord.Client()
logger = create_logger(bot_name)

hooks = {
    "text"  : lambda m: len(m.attachments) == 0,
    "images": lambda m: len(m.attachments) >  0,
    }

jokes = [
    "I was going to attend the clairvoyants meeting, but it was canceled due to unforseen events.",
    "Two cannibals are eating a clown. One cannibal turns to the other and asks 'Does this taste funny to you?'",
    "Two atoms are in a bar. One says, 'I think I lost an electron.' The other says, 'Are you sure?' To which the other replies 'I'm positive.'",
    "A neutron walks into a bar. 'How much for a drink here, anyway?' To which the bartender responds, 'For you, no charge.'",
    "I once visited a crematorium that gave discounts for burn victims.",
    "Photons have mass? I didn't even know they were Catholic.",
    "It's common knowledge that irradiated cats have 18 half-lives.",
    "Did you know the best contraceptive for old people is nudity?",
    ]

@register_command
async def perms(msg, mobj):
    """
    Check a user's permissions
    Print all of the user's permissions in a readable line-by-line format
    """
    try:
        perms = mobj.channel.permissions_for(mobj.author)
        lines = [
            "Administrator? {}".format(perms.administrator),
            "Manage server? {}".format(perms.manage_server),
            "Manage messages? {}".format(perms.manage_messages),
            "Attach files? {}".format(perms.attach_files),
            ]
        return await client.send_message(mobj.channel, pre_text("\n".join(lines)))
    except Exception as ex:
        logger("!perms: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to check permissions")

@register_command
async def clean(msg, mobj): 
    """
    This cleans all messages from the input channel
    This is only a command allowed for administrators
    Optional argument to purge non-images from a channel
    """
    try:
        perms = mobj.channel.permissions_for(mobj.author)
        if not perms.administrator:
            return await client.send_message(mobj.channel, "Admins only allowed to purge")
        lamb = hooks[msg] if msg in hooks else None
        await client.purge_from(mobj.channel, limit=30000, check=lamb)
        return
    except Exception as ex:
        logger("!clean: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to execute action")

@register_command
async def joke(msg, mobj):
    """
    Returns a random joke
    The real joke is this help message *ba-dum tsh*
    """
    return await client.send_message(mobj.channel, choice(jokes))
    

setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end

