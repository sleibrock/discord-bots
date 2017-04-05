#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Science Bot

An improved version of the old graph-bot
using the new class-based library

Spoilers: will use the most memory out of all bots
"""

from Bot import ChatBot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt
from sympy import sympify, Abs
from sympy.plotting import plot, plot3d
from sympy.utilities.lambdify import lambdify
from mpmath import cplot
from os import remove as f_remove

class ScienceBot(ChatBot):
    SAMPLE_SIZE = 2000 # complex graphing, affects render times
    
    def __init__(self, name):
        super(ScienceBot, self).__init__(name)
        self.filegen = self._create_filegen(self.name)

    @staticmethod
    def make_graph(expr, s, color='b'):
        """
        Create a plot based on whether it's a 1-var or 2-var expression
        Return None of vars == 0 or vars > 2
        """
        symcount = len(expr.free_symbols)
        if len(expr.free_symbols) == 0 or len(expr.free_symbols) > 2:
            return None

        if symcount == 1:
            pass

        if symcount == 2:
            pass

        return

    @ChatBot.action
    async def graph(args, mobj):
        pass

    @ChatBot.action
    async def graphc(args, mobj):
        pass

    pass

if __name__ == "__main__":
    b = ScienceBot("science-bot")
    b.run()
    pass

# end
