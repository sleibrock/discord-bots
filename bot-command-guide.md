Bot Command Guide
=================

This is a guide on the bots, what they do and how to use them.
This is currently a work in progress.

## dumb-bot

Dumb-bot is a bare-bones Discord client Bot API. For every command he has
he executes an asynchronous action. His two most key features are scraping
from YouTube as well as DuckDuckGo. He was my first bot, and paved the way
for the future.

## remind-bot

Remind-bot is a bot that stores reminders and dispatches them to users when
the reminder expires. You feed remind-bot a delta of when you want to be
alerted and he will remind you at that time. He checks every minute for stored
reminders and will dispatch and clear the reminder once it's finished.

Reminders are not encrypted and are stored in plaintext. For this reason,
please don't store anything private in reminders like passwords, credit cards,
social security numbers.

## graph-bot

Graph-bot is a bot with a focus on using `matplotlib` and `sympy` together to
interpret user-fed data and translate it into a visual graph. These functions
can probaby generate a lot of errors so don't be surprised if you can't graph
correctly the first time.
