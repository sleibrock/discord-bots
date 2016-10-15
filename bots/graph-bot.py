#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
import matplotlib
matplotlib.use('Agg')
from sympy.parsing.sympy_parser import parse_expr
from sympy.plotting import plot
from os import remove

bot_name = "graph-bot"
client = discord.Client()
logger = create_logger(bot_name)
bot_data = create_filegen(bot_name)

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
    args = [msg.content.lower().strip(), msg.id, msg.channel]
    binds = {'!graph' : graph,
             '!graph2': graph2,
             '!matrix': matrix,}
    for k, v in binds.items():
        if args[0].startswith(k):
            return await v(*args)
    return

async def graph(msg, mid, mchan):
    """
    Do a 2D-plot of a user's given function
    """
    try:
        firstp = msg.split(",") # seperate equation from additional args
        func = firstp[0].split(" ")[1] # yank the function from the com
        expr = parse_expr(func)
        graph = plot(expr, xlim=(-5,5), ylim=(-5,5), show=False)
        graph.save(bot_data("{}.png".format(mid)))
        await client.send_file(mchan, bot_data( "{}.png".format(mid)))
        remove(bot_data("{}.png".format(mid)))
    except Exception as ex:
        logger("Failed to render user function: {}".format(ex))
    return await client.send_message(mchan, "Failed to render graph")

async def graph2(msg, mid, mchan):
    """
    Do a 3D-plot of a user's given function
    TODO: actually implement this
    """
    return await client.send_message(mchan, "Not implemented")

async def matrix(msg, mid, mchan):
    """
    Plot a given matrix
    TODO: make it happen?
    """
    return await client.send_message(mchan, "Not implemented")

if __name__ == "__main__":
    try:
        key = argv[1]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client.start(read_key(key)))
    except Exception as e:
        logger("Whoops! {}".format(e))
    except SystemExit:
        logger("Leaving this existence behind")
    except KeyboardInterrupt:
        logger("Ouch!")
    finally:
        logger("Exiting")
        loop.run_until_complete(client.logout())
        loop.stop()
        loop.close()
    quit()

# end

