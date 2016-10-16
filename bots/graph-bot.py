#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Graph-bot

Creates graphs, stores them in the data folder,
then removes them once uploaded
"""

from botinfo import *
import matplotlib
matplotlib.use('Agg')
from sympy import sympify, Abs
from sympy.plotting import plot
from os import remove as f_remove

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
    splits = msg.content.lower().strip().split(" ")
    key = splits.pop(0)
    rest = " ".join(splits) if len(splits) > 0 else ""
    args = [rest, msg.id, msg.channel]
    binds = {'!graph' : graph,
             '!graph2': graph2,
             '!matrix': matrix,}
    for k, v in binds.items():
        if key == k:
            if not len(rest):
                return await client.send_message(args[2], pre_text(v.__doc__))
            else:
                return await v(*args)
    return

async def graph(msg, mid, mch):
    """
    Do a 2D-plot of a user's given function
    Ex1: !graph cos(x)*10
    Ex2: !graph cos(x)*10, xmax=10, xmin=-7
    """
    s = {'xmax':10.0, 'xmin':-10.0,
         'ymax':10.0, 'ymin':-10.0,}
    try:
        firstp = msg.split(",") # seperate equation from additional args
        func = firstp[0]
        if len(firstp) > 1:
            for p in firstp[1:]:
                print(p.strip())
                arg, val = p.strip().split("=")
                if arg in s.keys():
                    s[arg] = float(val)
                else:
                    return await client.send_message(mch, "Invalid arguments")
                if not all([isinstance(x, float) for x in s.values()]):
                    return await client.send_message(mch, "Invalid arguments")
        expr = sympify(func)
        var = list(expr.free_symbols)[0]

        # Replace the unknown 'abs' with the 'Abs' - I hate this
        expr = expr.replace(sympify("abs(x)").func, Abs)

        graph = plot(expr, (var, s["xmin"], s["xmax"]),
                     xlim=(s["xmin"], s["xmax"]),
                     ylim=(s["ymin"], s["ymax"]),
                     legend=True,
                 autoscale=False, show=False)
        graph.save(bot_data("{}.png".format(mid)))
        await client.send_file(mch, bot_data( "{}.png".format(mid)))
        f_remove(bot_data("{}.png".format(mid)))
        return
    except Exception as ex:
        logger("!graph: {}".format(ex))
    return await client.send_message(mch, "Failed to render graph")

async def graph2(msg, mid, mch):
    """
    Do a 3D-plot of a user's given function
    TODO: actually implement this
    """
    return await client.send_message(mch, "Not implemented")

async def graphi(msg, mid, mch):
    """
    Graph a complex equation
    TODO: this whole function
    """
    return await client.send_message(mch, "Not implemented")

async def calculus(msg, mid, mch):
    """
    Plot a function, it's first derivative, and it's first anti-derivative
    TODO: this one but it shouldn't take forever
    """
    return await client.send_message(mch, "Not implemented")

async def matrix(msg, mid, mch):
    """
    Plot a given matrix
    TODO: make it happen?
    """
    return await client.send_message(mch, "Not implemented")

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

