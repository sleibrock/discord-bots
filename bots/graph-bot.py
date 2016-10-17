#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Graph-bot

Creates graphs, stores them in the data folder,
then removes them once uploaded

This will probably eat up 100MB of memory
"""

from botinfo import *
import matplotlib
matplotlib.use('Agg') # only way to render without an Xserver running
from sympy import sympify, Abs
from sympy.plotting import plot, plot3d
from sympy.utilities.lambdify import lambdify
from mpmath import cplot
from os import remove as f_remove
from ast import literal_eval

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

def monkey_patch_function(expr):
    """
    Name says it all
    Monkey patch any functions with bad func names (abs -> Abs)
    """
    return expr.replace(sympify("abs(x)").func, Abs)

def create_plot(expr, s, color='b'):
    """
    Create a plot based on whether it's 1-variable or 2-variable
    """
    if len(expr.free_symbols) == 1:
        var1 = list(expr.free_symbols)[0]
        p = plot(expr, (var1, s["xmin"], s["xmax"]),
                     xlim=(s["xmin"], s["xmax"]),
                     ylim=(s["ymin"], s["ymax"]),
                     legend=True, show=False,
                     line_color=color)
    elif len(expr.free_symbols) == 2:
        var1, var2 = list(expr.free_symbols)
        p = plot3d(expr, (var1, s["xmin"], s["xmax"]),
                         (var2, s["ymin"], s["ymax"]),
                         xlim=(s["xmin"], s["xmax"]),
                         ylim=(s["ymin"], s["ymax"]),
                         title=str(expr), show=False)
    else:
        raise IndexError("Too many or too little variables")
    return p

@client.event
async def on_message(msg):
    """
    Dispatch commands to the respective functions
    Map a keyword to a function and pass the message values to the func
    """
    splits = msg.content.lower().strip().split(" ")
    k = splits.pop(0)
    rest = " ".join(splits) if len(splits) > 0 else ""
    args = [rest, msg.id, msg.channel]
    binds = {'!graph'    : graph,
             '!graphc'   : graphc,
             '!integrate': integrate,
             '!derive'   : derive,
             '!matrix'   : matrix,}
    if k in binds:
        if not len(rest):
            return await client.send_message(args[2], pre_text(binds[k].__doc__))
        else:
            return await binds[k](*args)
    return

async def graph(msg, mid, mch):
    """
    Do a 2D-plot of a user's given function
    Ex1: !graph cos(x)*10
    Ex2: !graph cos(x)*10, xmax=10, xmin=-7
    """
    s = {'xmax':10.0, 'xmin':-10.0,
         'ymax':10.0, 'ymin':-10.0,}
    fname = bot_data("{}.png".format(mid))
    try:
        firstp = msg.split(",") # seperate equation from additional args
        func = firstp[0]
        if len(firstp) > 1:
            for p in firstp[1:]:
                arg, val = p.strip().split("=")
                if arg in s.keys():
                    s[arg] = float(val)
                else:
                    return await client.send_message(mch, "Invalid arguments")
                if not all([isinstance(x, float) for x in s.values()]):
                    return await client.send_message(mch, "Invalid arguments")
        expr = monkey_patch_function(sympify(func))
        graph = create_plot(expr, s)
        graph.save(fname)
        await client.send_file(mch, fname)
        f_remove(fname)
        return
    except Exception as ex:
        logger("!graph: {}".format(ex))
    return await client.send_message(mch, "Failed to render graph")

async def graphc(msg, mid, mch):
    """
    Graph a complex equation (using mpmath functions and plotting)
    Equations should map to the complex domain
    Ex: !graphc gamma(x)
    """
    fname = bot_data("{}.png".format(mid))
    sample_size = 1000
    try:
        firstp = msg.split(",")
        func = firstp[0]
        expr = sympify(func)
        var = list(expr.free_symbols)[0]
        expr = monkey_patch_function(expr) # still apply the same fixes
        lamb = lambdify(var, expr, modules=["mpmath"]) # force mpmath functions
        cplot(lamb, points=sample_size, file=fname)
        await client.send_file(mch, fname)
        f_remove(fname)
        return
    except Exception as ex:
        logger("!graphc: {}".format(ex))
    return await client.send_message(mch, "Failed to render graph")

async def calculus(msg, mid, mch, lam, col):
    """
    Base function to perform some kind of calculus
    :lam is the type of operation we want, should be a lambda function
    :col is the color of the plot we want to have
    """
    s = {'xmax':10.0, 'xmin':-10.0,
         'ymax':10.0, 'ymin':-10.0,}
    fname = bot_data("{}.png".format(mid))
    try:
        firstp = msg.split(",")
        func = firstp[0]
        expr = monkey_patch_function(sympify(func))
        var = list(expr.free_symbols)[0]
        graph = create_plot(expr, s)
        graph.extend(create_plot(lam(expr), s, color=col))
        graph.save(fname)
        await client.send_file(mch, fname)
        return
    except Exception as ex:
        logger("!calculus: {}".format(ex))
    return await client.send_message(mch, "Failed to render graph")

def integrate(msg, mid, mch):
    """
    Integrate a given function to yield it's anti-derivative
    Function must be continuous, and all results technically have a hidden constant
    Ex: !integrate cos(x)**2
    """
    return calculus(msg, mid, mch, lambda e: e.integrate(), 'r')

def derive(msg, mid, mch):
    """
    Derive a given function to yield it's first derivative
    Note: must be a continuous function
    Ex: !derive x^3
    """
    return calculus(msg, mid, mch, lambda e: e.diff(), 'g')

async def matrix(msg, mid, mch):
    """
    Plot a given matrix using Numpy matrices and ast.literal_eval
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

