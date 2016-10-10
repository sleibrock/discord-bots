#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
from time import time, mktime
from datetime import datetime, timedelta

# bot info and whatever who cares
bot_name = "remind-bot"
client = discord.Client()
logger = create_logger(bot_name)
bot_data = create_filegen(bot_name)

# only support weeks, days and hours right now
# months and years involves specific edge cases and leap years etc
units = ["weeks", "days", "hours", "minutes"]
units.extend([t[:-1] for t in units])

# settings
settings = {"readloop":True,
            "max_rem": 5
            }

helpmsg = pre_text("""Remind-bot
Hold up to 5 reminders for remind-bot to remind you about
Usage: <message> !! <time span>
Example: dont drink that poison!! 3 hours 20 minutes
Clear:   !!clear
List:    !!list

Disclaimer: reminders are not encrypted, they are stored in plaintext
""")

def pretty_res_date(res_date):
    """
    Convert a res date list into a pretty list for printing
    If k==0 then we bump the index up to a single unit

    i + (units.length/2) * int(k==0) -> 1 minute instead of 1 minutes
    """
    result = ["{} {}".format(k, units[i+((len(units)//2)*int(k==1))])
              for i, k in enumerate(res_date) if k != 0]
    return ", ".join(result)

def time_remaining(utime):
    """
    Invert a unix time stamp and convert it to a "time remaining"
    stamp representing weeks/days/hours/minutes
    Check if the time stamp already expired (if utime <= cur_time)
    """
    pass

def create_offset(time_arr):
    """
    Turn a time array of ints into a unix time stamp
    representing the reminder's time delta
    """
    delta = timedelta(days=time_arr[1], weeks=time_arr[0], hours=time_arr[2], minutes=time_arr[3])
    offset = datetime.now() + delta
    return mktime(offset.timetuple())

@client.event
async def on_ready():
    """
    Basic function to log in and set up data
    """
    if not setup_bot_data(bot_name, logger):
        logger("Failed to set up {}'s folder".format(bot_name))
        client.close()
    settings["readloop"] = True
    return logger("Connection status: {}".format(client.is_logged_in))

@client.event
async def on_error(msg):
    """
    When bot receives a fatal websocket error, close the
    reading thread down and close the client
    """
    settings["readloop"] = False
    client.close()
    return logger("Discord error: {}".format(msg))

@client.event
async def on_message(msg):
    """
    Function to handle message dispatch
    For commands we check if certain ones are equal length to desired commands
    """
    auth = str(msg.author.id)
    m = msg.content.lower().strip()

    if "!!" not in m:
        return

    if m == "!!help":
        return await client.send_message(msg.channel, helpmsg)

    if m == "!!clear":
        with open(bot_data(auth), "w") as f:
            f.write("")
        return await client.send_message(msg.author, "Reminders cleared.")

    # TODO: convert utimes into remaining time for this function
    if m.startswith('!!list') and len(m) == 6:
        pass

    # Check if the input string doesn't match our conditions
    if m.count("!!") != 1 or len(m) < 10:
        return

    # strip the message from the time span
    dmsg, tmsg = m.split("!!")

    # Transform strings that look like 2d 3h into timedeltas
    splits = tmsg.strip().split(" ")

    # Stop if no time span was given (ie: empty list or less than 2 units of text)
    if not splits or len(splits) < 2:
        return

    # convert a time span string into an array of ints
    res = [0,0,0,0] # weeks, days, hours, minutes
    while len(splits) != 0:
        num = splits.pop(0) # check if it's a number
        if not num.isnumeric():
            return
        unit = splits.pop(0) # check what unit this is
        if unit not in units:
            return
        index = units.index(unit) % (len(units)//2) # oddest looking code here
        if res[index] != 0:
            return
        res[index] = int(num)

    # check to see if a user gave us all 0 units (0 hours, 0 days, etc)
    if not any(res):
        return await client.send_message(msg.author, "Cannot use zero-time delta")

    # Read a users file to scan for their previous reminders
    if not isfile(bot_data(auth)):
        lines = []
    else:
        with open(bot_data(auth), "r") as f:
            lines = f.readlines()
        if len(lines) >= settings["max_rem"]:
            return await client.send_message(msg.author, "Full! Clear your list with '!!clear'")

    lines.append("{},{}".format(int(create_offset(res)), dmsg))
    with open(bot_data(auth), "w") as f:
        f.write("\n".join(lines))

    return await client.send_message(msg.author, "Reminder set for {}".format(pretty_res_date(res)))

async def scan_reminders():
    """
    Function to scan all users reminder files
    Builds up a queue then dispatches reminders to each reminder in the queue
    """
    while settings["readloop"]:
        await asyncio.sleep(60) # scan once every 5 minutes
        queue = list()
        for f in listdir(bot_folder(bot_name)):
            with open(bot_data(f), 'r') as df:
                lines = df.readlines()
            rewrite = list()
            for line in [l.strip() for l in lines if l.strip() != ""]:
                tstamp, msg = line.split(",")
                if int(tstamp) <= int(time()):
                    queue.append((f, msg))
                else:
                    rewrite.append(line)

            with open(bot_data(f), 'w') as df:
                df.write("\n".join(rewrite))

        if not client.is_logged_in or client.is_closed:
            settings["readloop"] = False
            return logger("Client is not logged in")

        # dispatch alerts that were queued
        for alert in queue:
            if not await send_message(*alert):
                logger("Couldn't dispatch message to {}".format(alert[0]))
    return logger("Reading thread closed")

async def send_message(uid, msg):
    """
    Dispatch a message to a given UID
    Discord does not allow for direct User object creation
    So we have to search in all servers for a user to match the UID
    Then send that user a message
    False if it could not send (invalid UID, network connection error...)
    """
    for server in client.servers:
        for user in server.members:
            if str(user.id) == uid:
                return await client.send_message(user, "This is your reminder for: {}".format(msg))
    return False

if __name__ == "__main__":
    try:
        argv.pop(0)
        key = argv.pop(0)
        loop = asyncio.get_event_loop()
        tasks = [scan_reminders(), client.start(read_key(key))]
        loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        logger("Whoops! {}".format(e))
    except SystemExit:
        logger("Leaving this existence behind")
    except KeyboardInterrupt:
        logger("Ouch!")
    finally:
        logger("Exiting")
        settings["readloop"] = False
        loop.run_until_complete(client.logout())
        loop.stop()
        loop.close()
        quit()

# end
