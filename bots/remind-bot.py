#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
from time import time, mktime
from datetime import datetime, timedelta

bot_name = "remind-bot"
client = discord.Client()
logger = create_logger(bot_name)
bot_data = create_filegen(bot_name)

# only support weeks, days and hours right now
# months and years involves specific edge cases and leap years etc
units = ["weeks", "days", "hours", "minutes"]
max_reminders = 5

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
    """
    result = ["{} {}".format(k, units[i]) for i, k in enumerate(res_date) if k != 0]
    return ", ".join(result)

def time_remaining(utime):
    pass

@client.event
async def on_ready():
    """
    Basic function to log in and set up data
    """
    if not setup_bot_data(bot_name, logger):
        logger("Failed to set up {}'s folder".format(bot_name))
        client.close()
    return logger("Connection status: {}".format(client.is_logged_in))

@client.event
async def on_message(msg):
    """
    Function to handle message dispatch
    For commands we check if certain ones are equal length to desired commands
    """
    auth = str(msg.author.id)
    m = msg.content.lower().strip()

    if m.startswith('!!help') and len(m) == 6:
        return await client.send_message(msg.channel, helpmsg)

    if m.startswith('!!clear') and len(m) == 7:
        with open(bot_data(auth), "w") as f:
            f.write("")
        return await client.send_message(msg.author, "Reminders cleared.")

    # TODO: convert utimes into remaining time for this function
    if m.startswith('!!list') and len(m) == 6:
        pass

    if "!!" in m and m.count("!!") == 1 and len(m) > 10:
        dmsg, tmsg = m.split("!!")
        
        # Transform strings that look like 2d 3h into timedeltas
        splits = tmsg.strip().split(" ")

        if not splits:
            return await client.send_message(msg.author, "You didn't input anything! Try '!!help'")

        res = [0,0,0,0] # weeks, days, hours, minutes
        while len(splits) != 0:
            num = splits.pop(0) # check if it's a number
            if not num.isnumeric():
                return await client.send_message(msg.author, "Invalid number '{}', try '!!help'".format(num))
            unit = splits.pop(0) # check what unit this is
            if unit not in units:
                return await client.send_message(msg.author, "Invalid unit '{}', try '!!help'".format(unit))
            index = units.index(unit) 
            if res[index] != 0:
                return await client.send_message(msg.author, "Unit already set for {}, try '!!help'".format(unit))
            res[index] = int(num)

        # check to see if a user gave us all 0 units (0 hours, 0 days, etc)
        if not any(res):
            return await client.send_message(msg.author, "Cannot use zero-time delta")

        # create a time delta and add it's unix time to our current time
        delta = timedelta(days=res[1], weeks=res[0], hours=res[2], minutes=res[3])
        now = datetime.now()
        offset = now + delta
        utime = mktime(offset.timetuple())

        # Read a users file to scan for their previous reminders
        if isfile(bot_data(auth)):
            with open(bot_data(auth), "r") as f:
                lines = f.readlines()
                if len(lines) >= max_reminders:
                    return await client.send_message(msg.author, "Full! Clear your list with 'remclear!'")
        else:
            lines = []        

        lines.append("{},{}".format(int(utime), dmsg))
        with open(bot_data(auth), "w") as f:
            f.write("\n".join(lines))

        return await client.send_message(msg.author, "Reminder set for {}".format(pretty_res_date(res)))

async def scan_reminders():
    """
    Function to scan all users reminder files
    Builds up a queue then dispatches reminders to each reminder in the queue
    """
    while True:
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

        # dispatch alerts that were queued
        for alert in queue:
            r = await send_message(*alert)
            if not r:
                logger("Couldn't dispatch message to {}".format(alert[0]))

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
        loop.run_until_complete(client.logout())
        loop.stop()
        loop.close()
    quit()

# end
