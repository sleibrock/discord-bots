#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Hacker bot

Designed as a way to interact with the host machine
Also comes with a Lis.py interpreter (thanks Peter Norvig)
Although it's more of a Racket-style interpreter with some new stuffs
Requires: cowsay installed on system
"""

from botinfo import *
from bs4 import BeautifulSoup as BS
from requests import get as re_get
from random import choice, random, randint

# Lisp interpreter imports
import math
import operator as op
from functools import reduce

bot_name = "hacker-bot"
client   = discord.Client()
logger   = create_logger(bot_name)
bot_data = create_filegen(bot_name)
max_slen = 300
max_data = 100
max_stak = 10

## Lisp Interpreter section 
Symbol = str          # A Lisp Symbol is implemented as a Python str
List   = list         # A Lisp List is implemented as a Python list
Number = (int, float) # A Lisp Number is implemented as a Python int or float
def tokenize(chars):
    """
    Convert a string of characters into a list of tokens
    Support for Racket [] and {} closings
    """
    chars = chars.replace('[', ' ( ').replace(']', ' ) ')
    chars = chars.replace('{', ' { ').replace('}', ' ) ')
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    """
    Numbers become numbers; every other token is a symbol
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return lispeval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

def compose(*list_of_funcs):
    """
    Compose a list of functions into a singular function
    """
    if not all(filter(callable, list_of_funcs)):
        raise SyntaxError("Non-composable type given")
    def whatever(in_var):
        for func in list_of_funcs:
            in_var = func(in_var)
        return in_var
    return whatever

def standard_env():
    """
    An environment with some Scheme standard procedures
    Updated for Python 3 specifics and a lot more Lispy stuff
    """
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        'append'     : op.add,  
        'eq?'        : op.is_, 
        'equal?'     : op.eq, 
        'not'        : op.not_,
        'abs'        : abs,
        'length'     : len, 
        'sum'        : sum,
        'max'        : max,
        'min'        : min,
        'reduce'     : reduce,
        'random'     : random,
        'randint'    : randint,
        'choice'     : choice,
        'round'      : round,
        'compose'    : compose,
        'id'         : lambda x   : x,
        'eq?'        : lambda *x  : reduce(op.is_, x),
        'equal?'     : lambda *x  : reduce(op.eq, x),
        '+'          : lambda *x  : reduce(op.add, x),
        '-'          : lambda *x  : reduce(op.sub, x),
        '*'          : lambda *x  : reduce(op.mul, x),
        '/'          : lambda *x  : reduce(op.truediv, x),
        '>'          : lambda *x  : reduce(op.gt, x),
        '<'          : lambda *x  : reduce(op.lt, x),
        '>='         : lambda *x  : reduce(op.ge, x),
        '<='         : lambda *x  : reduce(op.le, x),
        '='          : lambda *x  : reduce(op.eq, x),
        'or'         : lambda *x  : reduce(lambda x, y: x or y, x),
        'and'        : lambda *x  : reduce(lambda x, y: x and y, x),
        'add1'       : lambda x   : x + 1,
        'sub1'       : lambda x   : x - 1,
        'range'      : lambda x   : list(range(x)),
        'span'       : lambda x   : list(range(x, y)),
        'enum'       : lambda x   : list(enumerate(x)),
        'zip'        : lambda x   : list(zip(x)),
        'apply'      : lambda f,x : f(*x),
        'begin'      : lambda *x  : x[-1],
        'car'        : lambda x   : x[0],
        'cdr'        : lambda x   : x[1:], 
        'head'       : lambda x   : x[0],
        'tail'       : lambda x   : x[1:],
        'cons'       : lambda x, y: [x] + y,
        'list'       : lambda *x  : list(x), 
        'map'        : lambda f, x: list(map(f, x)),
        'filter'     : lambda f, x: list(filter(f, x)),
        'zero?'      : lambda x   : x == 0,
        'empty?'     : lambda x   : len(x) == 0,
        'pair?'      : lambda x   : len(x) == 2,
        'procedure?' : lambda x   : callable(x),
        'number?'    : lambda x   : isinstance(x, Number),   
        'symbol?'    : lambda x   : isinstance(x, Symbol),
        'list?'      : lambda x   : isinstance(x,list), 
    })
    return env

global_env = standard_env()

def lispeval(x, env=global_env):
    """
    Evaluate an expression in an environment
    """
    if isinstance(x, Symbol):      # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x                
    elif x[0] == 'quote':          # quotation
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # conditional
        (_, test, conseq, alt) = x
        exp = (conseq if lispeval(test, env) else alt)
        return lispeval(exp, env)
    elif x[0] == 'define':         # definition
        (_, var, exp) = x
        env[var] = lispeval(exp, env)
    elif x[0] == 'set!':           # assignment
        (_, var, exp) = x
        env.find(var)[var] = lispeval(exp, env)
    elif x[0] == 'lambda':         # procedure
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # procedure call
        proc = lispeval(x[0], env)
        args = [lispeval(arg, env) for arg in x[1:]]
        return proc(*args)

def schemestr(exp):
    """
    Convert a Python object back into a Scheme-readable string
    """
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')' 
    return str(exp)

@register_command
async def e(msg, mobj):
    """
    Interpret a Lisp expression using Python
    Example: !lisp (+ 1 2)
    """
    try:
        result = lispeval(parse(msg))
        if len(str(result)) + len(msg) > 1900:
            return await client.send_message(mobj.channel, "Output too large")
        return await client.send_message(mobj.channel, pre_text("{}\n => {}".format(msg, result)))
    except Exception as ex:
        return await client.send_message(mobj.channel, pre_text("{}: {}".format(type(ex).__name__, ex)))
    return await client.send_mesage(mobj.channel, "Failed to compute expression")

## end lisp section
            
@register_command
async def test(msg, mobj):
    print(client.messages)
    print(len(client.messages))
    print("last message was: {}".format(get_last_message(mobj.channel).content))
    return await client.send_message(mobj.channel, "test")

@register_command
async def uptime(msg, mobj):
    """
    Return the uptime of the host system
    """
    return await client.send_message(mobj.channel, pre_text(call("uptime")))

@register_command
async def free(msg, mobj):
    """
    Return how much memory is free
    """
    return await client.send_message(mobj.channel, pre_text(call("free -m")))

@register_command
async def vmstat(msg, mobj):
    """
    Return raw memory stats from `vmstat`
    """
    return await client.send_message(mobj.channel, pre_text(call("vmstat")))

@register_command
async def uname(msg, mobj):
    """
    Return `uname -a` showing system and kernel version
    """
    return await client.send_message(mobj.channel, pre_text(call("uname -a | cowsay")))

@register_command
async def cal(msg, mobj):
    """
    Return the current month calendar
    """
    return await client.send_message(mobj.channel, pre_text(call("cal")))

@register_command
async def sed(msg, mobj):
    """
    Sed the previous user's message (as opposed to just editing it)
    Example: !sed s/hi/hello/g
    """
    if msg == "":
        return
    auth = mobj.author.id
    chan = mobj.channel
    last_m = get_last_message(client, chan, auth).content.strip().replace("\"", "'")
    return await client.send_message(chan, pre_text(call("echo \"{}\" | sed -s {}".format(last_m, msg))))

# The Git section
@register_command
async def update(msg, mobj):
    """
    Execute a `git pull` to update the code
    If there was a successful pull, the bot will quit and be restarted later
    Example: !update
    """
    print(msg)
    result = call("git pull")
    await client.send_message(mobj.channel, pre_text(result))
    if result.strip() == "Already up-to-date.":
        return
    logger("Restarting self")
    client.close()
    return quit()

@register_command
async def commits(msg, mobj):
    """
    Execute a `git log --oneline --graph --decorate=short | head -n 5`
    Example: !commits
    """
    return await client.send_message(
        mobj.channel, pre_text(call("git log --oneline --graph --decorate=short | head -n 5")))

# The Cowsay section for cowtagging and cowsay
@register_command
async def cowtag(msg, mobj):
    """
    Find the message before this one and add it to our cow list
    Example: !cowtag
    """
    chan = mobj.channel
    cowlist = bot_data("{}.txt".format(chan.id))
    last_m = get_last_message(client, chan)
    if last_m is None:
        return await client.send_message(chan, "Couldn't tag last message")
    last_m = last_m.content.replace("\n", " ").replace("\r", " ").strip()[:max_slen]
    last_m = last_m.replace("\"", "'")
    lines = read_lines(cowlist)
    lines.append(last_m)
    if len(lines) > max_data:
        lines.pop(0)
    if not write_lines(cowlist, lines):
        return await client.send_message(chan, "Error writing to file")
    return await client.send_message(chan, "Bagged and tagged")

@register_command
async def cowsay(msg, mobj):
    """
    Return a random cowsay message
    Example: !cowsay
    """
    chan = mobj.channel.id
    cowlist = bot_data("{}.txt".format(chan))
    cowlines = read_lines(cowlist)
    if not cowlines:
        return await client.send_message(mobj.channel, "No cow messages here")
    rand = choice(cowlines)
    if rand.strip() == "":
        return await client.send_message(mobj.channel, "No cow messages here")
    return await client.send_message(mobj.channel, pre_text(call("echo \"{}\" | cowsay".format(rand))))

setup_all_events(client, bot_name, logger)
if __name__ == "__main__":
    run_the_bot(client, bot_name, logger)
