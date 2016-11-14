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
import matplotlib.pylab as plt
from sympy import sympify, Abs
from sympy.plotting import plot, plot3d
from sympy.utilities.lambdify import lambdify
from mpmath import cplot
from numpy import matrix as np_matrix
from os import remove as f_remove
from ast import literal_eval

bot_name = "graph-bot"
client = discord.Client()
logger = create_logger(bot_name)
bot_data = create_filegen(bot_name)
sample_size = 2000 # used for complex graphing

def monkey_patch_function(expr):
    """
    Name says it all
    Monkey patch any functions with bad func names (abs -> Abs)
    If anything else needs to be fixed, goes here
    """
    return expr.replace(sympify("abs(x)").func, Abs)

def create_plot(expr, s, color='b'):
    """
    Create a plot based on whether it's 1-variable or 2-variable
    Raise Index error if we don't have any variables, or more than 2
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

@register_command
async def graph(msg, mobj):
    """
    Do a 2D-plot of a user's given function
    Ex1: !graph cos(x)*10
    Ex2: !graph cos(x)*10, xmax=10, xmin=-7
    """
    s = {'xmax':10.0, 'xmin':-10.0,
         'ymax':10.0, 'ymin':-10.0,}
    fname = bot_data("{}.png".format(mobj.author.id))
    try:
        firstp = msg.split(",") # seperate equation from additional args
        func = firstp[0]
        if len(firstp) > 1:
            for p in firstp[1:]:
                arg, val = p.strip().split("=")
                if arg in s.keys():
                    s[arg] = float(val)
                else:
                    return await client.send_message(mobj.channel, "Invalid arguments")
                if not all([isinstance(x, float) for x in s.values()]):
                    return await client.send_message(mobj.channel, "Invalid arguments")
        graph = create_plot(monkey_patch_function(sympify(func)), s)
        graph.save(fname)
        await client.send_file(mobj.channel, fname)
        f_remove(fname)
        return
    except Exception as ex:
        logger("!graph: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to render graph")

@register_command
async def graphc(msg, mobj):
    """
    Graph a complex equation (using mpmath functions and plotting)
    Equations should map to the complex domain
    Ex: !complex gamma(x)
    """
    fname = bot_data("{}.png".format(mobj.author.id))
    try:
        firstp = msg.split(",")
        func = firstp[0]
        expr = sympify(func)
        var = list(expr.free_symbols)[0]
        lamb = lambdify(var, monkey_patch_function(sympify(func)), modules=["mpmath"])
        cplot(lamb, points=sample_size, file=fname)
        await client.send_file(mobj.channel, fname)
        f_remove(fname)
        return
    except Exception as ex:
        logger("!graphc: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to render graph")

async def calculus(msg, mobj, lam, col):
    """
    Base function to perform some kind of calculus
    :lam is the type of operation we want, should be a lambda function
    :col is the color of the plot we want to have
    """
    s = {'xmax':10.0, 'xmin':-10.0,
         'ymax':10.0, 'ymin':-10.0,}
    fname = bot_data("{}.png".format(mobj.author.id))
    try:
        firstp = msg.split(",")
        func = firstp[0]
        expr = monkey_patch_function(sympify(func))
        var = list(expr.free_symbols)[0]
        graph = create_plot(expr, s)
        graph.extend(create_plot(lam(expr), s, color=col))
        graph.save(fname)
        await client.send_file(mobj.channel, fname)
        f_remove(fname)
        return
    except Exception as ex:
        logger("!calculus: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to render graph")

@register_command
def integrate(msg, mobj):
    """
    Integrate a given function to yield it's anti-derivative
    Function must be continuous, and all results technically have a hidden constant
    Ex: !integrate cos(x)**2
    """
    return calculus(msg, mobj, lambda e: e.integrate(), 'r')

@register_command
def derive(msg, mobj):
    """
    Derive a given function to yield it's first derivative
    Note: must be a continuous function
    Ex: !derive x^3
    """
    return calculus(msg, mobj, lambda e: e.diff(), 'g')

@register_command
async def matrix(msg, mobj):
    """
    Interpret a user string, convert it to a list and graph it as a matrix
    Uses ast.literal_eval to parse input into a list
    """
    fname = bot_data("{}.png".format(mobj.author.id))
    try:
        list_input = literal_eval(msg)
        if not isinstance(list_input, list):
            raise ValueError("Not a list")
        m = np_matrix(list_input)
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.set_aspect('equal')
        plt.imshow(m, interpolation='nearest', cmap=plt.cm.ocean)
        plt.colorbar()
        plt.savefig(fname)
        await client.send_file(mobj.channel, fname)
        f_remove(fname)
        return
    except Exception as ex:
        logger("!matrix: {}".format(ex))
    return await client.send_message(mobj.channel, "Failed to render graph")

setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)

# end

