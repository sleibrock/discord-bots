#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
bot_name = "remind-bot"
client = discord.Client()
logger = create_logger(bot_name)

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
async def on_message(message):
    if message.content.lower().startswith('remindme!'):
        await client.send_message(message.channel, 'Received message')
        return logger("Received a message!")

if __name__ == "__main__":
    try:
        argv.pop(0)
        key = argv.pop(0)
        client.run(read_key(key))
    except Exception as e:
        logger("Whoops! {}".format(e))
    except SystemExit:
        logger("Leaving this existence behind")
    except KeyboardInterrupt:
        logger("Ouch!")
    quit()

# end
