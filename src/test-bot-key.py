#!/usr/bin/env python
#-*- coding: utf-8 -*-

from botinfo import *
from sys import argv

client = discord.Client()

@client.event
async def on_ready():
    print("Logged in")
    print("ID: {}, Name: {}".format(client.user.id, client.user.name))
    client.logout()
    client.close()
    raise Exception

@client.event
async def on_error(err):
    print("Oops")
    client.logout()
    client.close()
    return False

if __name__ == "__main__":
    try:
        k = argv[1]
        client.run(k)
    except Exception as e:
        print("{} fail: {}".format(key, e))
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print("Don't touch that!")
    finally:
        print("Stopping")
    quit()

# end
